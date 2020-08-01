#include <array>
#include <cassert>
#include <fstream>
#include <future>
#include <iostream>
#include <random>
#include <utility>
#include <vector>

std::default_random_engine GLOBAL_RNG;

struct Score {
	int away = 0;
	int home = 0;
};

struct Pitcher {
	double H;
	double BB;
	double SO;
	double BF;
};

struct Batter {
	double AB;
	double H;
	double TWOB;
	double THREEB;
	double HR;
	double SO;
	double BA;
};


int MAXSCORE = 256;

class Team {
public:
	Team(const char *path);
	Pitcher& current_pitcher() { return m_pitcher; }
	Batter& next_batter() {
		Batter &btr = m_batters.at(m_idx);
		m_idx = (m_idx + 1) % 9;
		return btr;
	}
private:
	std::vector<Batter> m_batters;
	Pitcher m_pitcher;
	int m_idx = 0;
};

Team::Team(const char *path)
{
	std::ifstream infile(path);

	// First line is pitcher: H BB SO BF
	infile >> m_pitcher.H >> m_pitcher.BB >> m_pitcher.SO >> m_pitcher.BF;

	// Then nine batters: AB H TWOB THREEB HR SO BA
	for (int i = 0; i < 9; i++) {
		Batter b;
		infile >> b.AB >> b.H >> b.TWOB >> b.THREEB >> b.HR >> b.SO >> b.BA;
		m_batters.push_back(b);
	}

	assert(m_batters.size() == 9);

	infile.close();
}



enum Outcome {
	FirstBase = 0,
	SecondBase = 1,
	ThirdBase = 2,
	HomeRun = 3,
	TagOut = 4,
	FlyOut = 5,
	StrikeOut = 6,
	Walk = 7
};

class Field {
public:
	Field(bool overtime = false) : m_run_counter(0), m_bases({0, 0, 0}) {
		if (overtime)
			m_bases[1] = 1;
	}

	void advance(int n) {
		for (int i = 0; i < n; i++) {
			m_run_counter += m_bases[2];
			m_bases[2] = m_bases[1];
			m_bases[1] = m_bases[0];
			m_bases[0] = (i == 0)? 1 : 0;
		}
	}

	void out() {
		if (!m_bases[0] && !m_bases[1] && !m_bases[2])
			return;
		double f = m_bases[0] + m_bases[1] + m_bases[2];
		std::array<double, 3> ws;
		ws[0] = m_bases[0] / f;
		ws[1] = m_bases[1] / f;
		ws[2] = m_bases[2] / f;
		std::discrete_distribution<int> dist(ws.begin(), ws.end());
		int iout = dist(GLOBAL_RNG);
		m_bases[iout] = 0;
	}

	int runs() { return m_run_counter; }

private:
	int m_run_counter;
	std::array<int, 3> m_bases;
};

std::vector<double> compute_prob_dist(Pitcher &pitcher, Batter &batter)
{
	double prob_hit_p = pitcher.H / pitcher.BF;
	double prob_hit_b = batter.BA;
	double prob_hit = std::sqrt(prob_hit_p * prob_hit_b);

	double prob_walk = pitcher.BB / pitcher.BF;
	double prob_out = 1 - prob_hit - prob_walk;

	double prob_2B, prob_3B, prob_HR;
	if (batter.H > 0) {
		prob_2B = batter.TWOB / batter.H;
		prob_3B = batter.THREEB / batter.H;
		prob_HR = batter.HR / batter.H;
	} else {
		prob_2B = prob_3B = prob_HR = 0;
	}
	double prob_1B = 1 - prob_2B - prob_3B - prob_HR;

	double prob_strikeout_p = pitcher.SO / pitcher.BF;
	double prob_strikeout_b = batter.SO / batter.AB;
	double prob_strikeout = std::sqrt(prob_strikeout_p * prob_strikeout_b);
	double prob_flyout = 0.5 * (1 - prob_strikeout);
	double prob_tagout = prob_flyout;

	return {
		prob_hit * prob_1B,
		prob_hit * prob_2B,
		prob_hit * prob_3B,
		prob_hit * prob_HR,
		prob_out * prob_tagout,
		prob_out * prob_flyout,
		prob_out * prob_strikeout,
		prob_walk
	};
}


int simulate_at_bat(Field &field, Pitcher &pitcher, Batter &batter)
{
	std::vector<double> probs {compute_prob_dist(pitcher, batter)};
	std::discrete_distribution<int> dist {probs.begin(), probs.end()};

	int res = dist(GLOBAL_RNG);

	switch (res) {
	case Outcome::Walk:
	case Outcome::FirstBase:
		field.advance(1);
		break;
	case Outcome::SecondBase:
		field.advance(2);
		break;
	case Outcome::ThirdBase:
		field.advance(3);
		break;
	case Outcome::HomeRun:
		field.advance(4);
		break;
	case Outcome::TagOut:
		field.advance(1);
		field.out();
		break;
	default:
		break;
	}

	return res == TagOut || res == FlyOut || res == StrikeOut;
}

int play_half_inning(Team &offense, Team &defense, bool overtime = false)
{
	Field field(overtime);
	int outs = 0;
	while (outs < 3) {
		outs += simulate_at_bat(
			field, defense.current_pitcher(), offense.next_batter()
			);
	}
	return field.runs();
}

Score play_game(Team &away, Team &home)
{
	Score score;

	for (int i = 0; i < 10 or score.away == score.home; i++) {
		score.away += play_half_inning(away, home, i > 9);
		if ((i < 9) or (score.away >= score.home)) {
			score.home += play_half_inning(home, away, i > 9);
		}
	}

	return score;
}

typedef std::vector<int> Hist;

void add_inplace(Hist &to, Hist &from)
{
	if (to.size() != from.size()) {
		std::cerr << "size mismatch\n";
		return;
	}

	for (size_t i = 0; i < to.size(); i++)
		to[i] += from[i];
}

// TODO gotta use a 2d hist
std::pair<Hist, Hist> worker(Team &away, Team &home, int nsim)
{
	int max = MAXSCORE;

	std::vector<int> h_away(max + 1, 0);
	std::vector<int> h_home(max + 1, 0);

	for (int i = 0; i < nsim; i++) {
		Score sco = play_game(away, home);
		if (sco.away > max)
			sco.away = max;
		h_away[sco.away] += 1;
		if (sco.home > max)
			sco.home = max;
		h_home[sco.home] += 1;
	}

	return std::make_pair(h_away, h_home);
}

// Score most_probable_score_MT(Team &away, Team &home, int sims_per_thread=100000, int thread_n=2)
double compute_home_win_probability(Team &away, Team &home, int sims_per_thread=100000, int thread_n=2)
{
	std::vector<std::future<std::pair<Hist, Hist>>> pool;
	for (int i = 0; i < thread_n; i++) {
		pool.emplace_back(std::async(worker, std::ref(away), std::ref(home), sims_per_thread));
	}

	Hist runs_away(MAXSCORE + 1, 0);
	Hist runs_home(MAXSCORE + 1, 0);
	for (auto &fut : pool) {
		auto pair = fut.get();
		add_inplace(runs_away, pair.first);
		add_inplace(runs_home, pair.second);
	}

	// let's try the home win prob
	std::vector<double> p_away;
	double totw = 0;
	for (int x : runs_away)
		totw += x;
	for (int x : runs_away)
		p_away.push_back(x / totw);
	std::vector<double> p_home;
	totw = 0;
	for (int x : runs_home)
		totw += x;
	for (int x : runs_home)
		p_home.push_back(x / totw);

	std::vector<double> cdf_away;
	totw = 0;
	for (double x : p_away) {
		cdf_away.push_back(totw + x);
		totw += x;
	}

	// P(H > A) = sum_r P(H == r) * P(A < r)
	double hwp = 0;
	for (size_t i = 1; i < p_home.size(); i++) {
		hwp += p_home.at(i) * cdf_away.at(i - 1);
	}

	return hwp;
}



Score most_probable_score(Team &away, Team &home, int nsim=500000)
{
	int max = 100;

	std::vector<int> h_away(max, 0);
	std::vector<int> h_home(max, 0);

	Score mp;
	int max_away = -1;
	int max_home = -1;

	for (int i = 0; i < nsim; i++) {
		Score sco = play_game(away, home);
		h_away[sco.away] += 1;
		h_home[sco.home] += 1;

		if (h_away[sco.away] > max_away) {
			mp.away = sco.away;
			max_away = h_away[sco.away];
		}
		if (h_home[sco.home] > max_home) {
			mp.home = sco.home;
			max_home = h_home[sco.home];
		}
	}


	return mp;
}

int main(int argc, char *argv[])
{
	std::random_device rd;
	GLOBAL_RNG.seed(rd());
	if (argc != 3) {
		std::cerr << "Usage: " << argv[0] << " away-path home-path\n";
		return 1;
	}

	Team away(argv[1]);
	Team home(argv[2]);

	// Score sco = most_probable_score(away, home);
	// Score sco = most_probable_score_MT(away, home, 250000);
	double hwp = compute_home_win_probability(away, home, 250000);
	std::cout << hwp << std::endl;

	return 0;
}

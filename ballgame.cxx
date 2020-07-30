#include <array>
#include <random>
#include <utility>
#include <vector>

std::mt19937 GLOBAL_RNG;

struct Score {
	int away = 0;
	int home = 0;
};

class Batter;
class Pitcher;


class Team {
public:
	Pitcher& current_pitcher();
	Batter& next_batter();
};




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

private:
	int m_run_counter;
	std::array<int, 3> m_bases;
};

std::vector<double> compute_prob_dist(Pitcher &pitcher, Batter &batter);


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
}

Score play_game(Team &away, Team &home)
{
	Score score;

	for (int i = i; i < 10 or score.away == score.home; i++) {
		score.away += play_half_inning(away, home, i > 9);
		if ((i < 9) or (score.away >= score.home)) {
			score.home += play_half_inning(home, away, i > 9);
		}
	}

	return score;
}

int main()
{
	GLOBAL_RNG.seed(1234);
}

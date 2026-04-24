class ScoreCalculator:
    def calculate(self, options):
        return sum(option.score for option in options)


def calculate(self, options, duration=None):
    base_score = sum(option.score for option in options)
    speed_bonus = 0
    if duration and duration < 30:
        speed_bonus = 2
    return base_score + speed_bonus
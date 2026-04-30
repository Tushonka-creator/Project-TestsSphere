class ScoreCalculator:
    def calculate(self, options, duration=None, **kwargs):
        """
        Принимает список объектов AnswerOption и необязательную длительность.
        Возвращает сумму баллов с возможным бонусом за скорость.
        """
        base_score = sum(option.score for option in options)

        # Бонус за скорость: если тест пройден быстрее чем за 30 секунд,
        # добавляем +2 балла (как пример)
        speed_bonus = 0
        if duration and duration < 30:
            speed_bonus = 2

        return base_score + speed_bonus

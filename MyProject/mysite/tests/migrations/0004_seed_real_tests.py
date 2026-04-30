from django.db import migrations

def seed_tests(apps, schema_editor):
    Test = apps.get_model('tests', 'Test')
    Question = apps.get_model('tests', 'Question')
    AnswerOption = apps.get_model('tests', 'AnswerOption')
    ResultRange = apps.get_model('tests', 'ResultRange')

    # 1. Психологический тест: Тип темперамента
    temperament_test, _ = Test.objects.get_or_create(
        title="Ваш основной тип темперамента",
        slug="temperament-short",
        defaults={"description": "Узнайте, кто вы: сангвиник, холерик, флегматик или меланхолик. Краткий опросник на основе классических методик."}
    )

    t_q1, _ = Question.objects.get_or_create(test=temperament_test, text="Как вы обычно ведете себя в новой компании?", defaults={"order": 0})
    AnswerOption.objects.get_or_create(question=t_q1, text="Легко завожу знакомства, много шучу", score=3, defaults={"order": 0})
    AnswerOption.objects.get_or_create(question=t_q1, text="Присматриваюсь, вступаю в разговор не сразу", score=1, defaults={"order": 1})
    AnswerOption.objects.get_or_create(question=t_q1, text="Чувствую себя скованно, жду, когда заговорят со мной", score=0, defaults={"order": 2})

    t_q2, _ = Question.objects.get_or_create(test=temperament_test, text="Ваша реакция на резкое изменение планов?", defaults={"order": 1})
    AnswerOption.objects.get_or_create(question=t_q2, text="Раздражаюсь или бурно возмущаюсь", score=4, defaults={"order": 0})
    AnswerOption.objects.get_or_create(question=t_q2, text="Быстро адаптируюсь и ищу плюсы", score=3, defaults={"order": 1})
    AnswerOption.objects.get_or_create(question=t_q2, text="Спокойно принимаю как должное", score=2, defaults={"order": 2})

    t_q3, _ = Question.objects.get_or_create(test=temperament_test, text="Как вы обычно принимаете решения?", defaults={"order": 2})
    AnswerOption.objects.get_or_create(question=t_q3, text="Импульсивно, под влиянием момента", score=4, defaults={"order": 0})
    AnswerOption.objects.get_or_create(question=t_q3, text="Долго взвешиваю все 'за' и 'против'", score=1, defaults={"order": 1})

    ResultRange.objects.get_or_create(test=temperament_test, min_score=0, max_score=3, title="Меланхолик", defaults={"description": "Вы чувствительны, склонны к глубоким переживаниям. Часто бываете творческой натурой."})
    ResultRange.objects.get_or_create(test=temperament_test, min_score=4, max_score=6, title="Флегматик", defaults={"description": "Вы — скала спокойствия. Вас трудно вывести из себя, вы надежны и рациональны."})
    ResultRange.objects.get_or_create(test=temperament_test, min_score=7, max_score=9, title="Сангвиник", defaults={"description": "Живой, общительный и оптимистичный человек. Вы легко справляетесь с трудностями."})
    ResultRange.objects.get_or_create(test=temperament_test, min_score=10, max_score=100, title="Холерик", defaults={"description": "Вы — огонь! Энергичный, страстный. Вы прирожденный лидер."})

    # 2. Тест на общую эрудицию
    erudition_test, _ = Test.objects.get_or_create(
        title="Тест на общую эрудицию",
        slug="erudition",
        defaults={"description": "Проверьте свои знания в области истории, науки и искусства."}
    )

    e_q1, _ = Question.objects.get_or_create(test=erudition_test, text="Кто из этих ученых сформулировал законы всемирного тяготения?", defaults={"order": 0})
    AnswerOption.objects.get_or_create(question=e_q1, text="Исаак Ньютон", score=10, defaults={"order": 0})
    AnswerOption.objects.get_or_create(question=e_q1, text="Альберт Эйнштейн", score=0, defaults={"order": 1})
    AnswerOption.objects.get_or_create(question=e_q1, text="Никола Тесла", score=0, defaults={"order": 2})

    e_q2, _ = Question.objects.get_or_create(test=erudition_test, text="Какой химический элемент является самым распространенным во Вселенной?", defaults={"order": 1})
    AnswerOption.objects.get_or_create(question=e_q2, text="Водород", score=10, defaults={"order": 0})
    AnswerOption.objects.get_or_create(question=e_q2, text="Кислород", score=0, defaults={"order": 1})
    AnswerOption.objects.get_or_create(question=e_q2, text="Азот", score=0, defaults={"order": 2})

    ResultRange.objects.get_or_create(test=erudition_test, min_score=0, max_score=10, title="Начинающий", defaults={"description": "Мир полон открытий! Вам стоит больше интересоваться историей и наукой."})
    ResultRange.objects.get_or_create(test=erudition_test, min_score=20, max_score=20, title="Эксперт", defaults={"description": "Блестящий результат! Вашему кругозору можно только позавидовать."})

class Migration(migrations.Migration):
    dependencies = [
        ('tests', '0003_add_user_to_submission'),
    ]
    operations = [
        migrations.RunPython(seed_tests),
    ]

class CalorieBotExceptions(Exception): 
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)

class UnrealisticCalorieValue(CalorieBotExceptions):
    detail = "Количество дневных калорий не может превышать 10000 калорий, и не может быть равно нулю!"


from django.db import models

class OHLC(models.Model):
    code = models.CharField(max_length=10)         # 종목 코드
    interval = models.CharField(max_length=10)     # '1m', '5m', ...
    timestamp = models.DateTimeField()             # 캔들 생성 시간

    open = models.IntegerField()
    high = models.IntegerField()
    low = models.IntegerField()
    close = models.IntegerField()

    class Meta:
        unique_together = ('code', 'interval', 'timestamp')  # 중복 방지

    def __str__(self):
        return f'{self.code} - {self.interval} - {self.timestamp}'

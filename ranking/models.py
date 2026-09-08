from django.db import models

class Ranking(models.Model):
    nome = models.CharField(max_length=3)
    pontos = models.IntegerField()
    fase_alcancada = models.IntegerField()
    tempo_segundos = models.FloatField()
    data_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pontos', 'tempo_segundos']

    def __str__(self):
        return f"{self.nome} - {self.pontos} pts"
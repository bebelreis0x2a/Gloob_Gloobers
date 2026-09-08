import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Ranking

@csrf_exempt
def registrar_pontuacao(request):
    if request.method == 'POST':
        dados = json.loads(request.body)
        novo_registro = Ranking.objects.create(
            nome=dados.get('nome', 'AAA'),
            pontos=dados.get('pontos', 0),
            fase_alcancada=dados.get('fase', 1),
            tempo_segundos=dados.get('tempo', 0.0)
        )
        return JsonResponse({'status': 'sucesso', 'id': novo_registro.id}, status=201)
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

def listar_ranking(request):
    top_10 = Ranking.objects.all()[:10]
    dados = [
        {
            'nome': item.nome,
            'pontos': item.pontos,
            'fase': item.fase_alcancada,
            'tempo': round(item.tempo_segundos, 1)
        }
        for item in top_10
    ]
    return JsonResponse({'ranking': dados}, status=200)
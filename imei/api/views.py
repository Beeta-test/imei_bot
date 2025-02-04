import requests
from rest_framework import views, status
from rest_framework.response import Response
from imei.settings import API_TOKEN, IMEICHECK_SANDBOX_TOKEN

API_URL = "https://api.imeicheck.net/v1/checks"


class IMEIView(views.APIView):
    """Эндпоинт для проверки IMEI."""

    def post(self, request):
        imei = request.data.get("imei")
        token = request.data.get("token")

        if not imei or not token:
            return Response({"error": "Параметры imei и token обязательны."},
                            status=status.HTTP_400_BAD_REQUEST)

        if token != API_TOKEN:
            return Response({"error": "Неверный токен."},
                            status=status.HTTP_401_UNAUTHORIZED)

        if not (imei.isdigit() and len(imei) == 15):
            return Response({"error": "Неверный формат IMEI. Должно быть 15 цифр."},
                            status=status.HTTP_400_BAD_REQUEST)

        headers = {
            "Authorization": f"Bearer {IMEICHECK_SANDBOX_TOKEN}",
            "Content-Type": "application/json",
            "Accept-Language": "ru"
        }
        payload = {"deviceId": imei, "serviceId": 15}

        try:
            external_response = requests.post(API_URL, json=payload, headers=headers, timeout=10)

            if external_response.status_code != 200:
                return Response({"error": "Ошибка во внешнем API.",
                                 "status_code": external_response.status_code,
                                 "response": external_response.text},
                                status=status.HTTP_502_BAD_GATEWAY)

            try:
                return Response(external_response.json(), status=status.HTTP_200_OK)
            except requests.exceptions.JSONDecodeError:
                return Response({"error": "Ошибка обработки JSON от API."},
                                status=status.HTTP_502_BAD_GATEWAY)

        except requests.RequestException as e:
            return Response({"error": "Ошибка при обращении к внешнему API.",
                             "detail": str(e)},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

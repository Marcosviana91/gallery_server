# Gallery Server API for ESP32-CAM
Projeto inspirado em https://randomnerdtutorials.com/esp32-cam-http-post-php-arduino/

## ESP32-CAM OV264O

Carregue o [scketch](main.ino) em seu dispositivo e salve o arquivo [esp32.txt](esp32.txt) na raiz do seu cartão SD.
```
DEVICE_UUID=String
WIFI_SSID=String
WIFI_PASSWORD=String
```
Complete WIFI_SSID e WIFI_PASSWORD com as credenciais de sua rede WiFi.
O valor de DEVICE_UUID deve ser obtido ao criar um novo dispositivo no site. (_pendente_)

### Funcionamento do Scketch
Ao iniciar o dispositivo 50 imagens são capturadas e enviadas ao servidor a cada 1 segundo, após isso, outras 50 a cada 3 segundos. Por fim o dispositivo entra em estado de hibernação (deep sleep) e deve ser reiniciado para repetir o ciclo.

## Servidor
> `docker compose up` para executar o projeto.
- POST `/api/upload/` \
O dispositivo envia uma imagem para a rota '__/api/upload/__' e no cabeçalho da requisição POST, uma chave '__Device-UUID__' com o valor de '_DEVICE_UUID_' salvo no arquivo  [esp32.txt](esp32.txt)
- GET `/api/images/` \
O servidor responde com um JSON. Uma chave 'dirs' onde o valor é uma lista de diratórios dessa pasta. Copie o nome de uma pasta e adicione ao endereço atual, repita até que seja retornado algum arquivo. Por fim, copie o nome de um arquivo, adicione ao endereço atual e remova a rota '__/api/__' do endereço, para acessar o arquivo.
> Site e App móvel pendente
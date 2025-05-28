# O que cada API faz e como executá-la
A API de Sensores em **Node.js** sorteia valores de temperatura e pressão em **/sensor-data** e manda um alerta para o módulo de eventos quando você chama **/alert**. 
Para rodar, entre em **sensor-api**, instale as dependências com **npm install** e inicie com **npm start** (porta 3000).

A API de Eventos Críticos em **Python** recebe esses alertas no **/event**, guarda tudo em memória e mostra a lista completa em **/events**. 
Suba com **python app.py** dentro de events-api depois de instalar as libs do requirements.txt (porta 5000).

A API de Logística em **PHP** devolve uma lista de equipamentos em **/equipments** e, em **/dispatch**, despacha um pedido urgente para a fila RabbitMQ. 
Execute entrando em **logistics-api**, rodando **composer install** e depois **php -S localhost:8000 index.php (porta 8000)**.

### Antes de iniciar os três serviços, confirme que Redis e RabbitMQ estejam em execução executando o docker-compose.yml do projeto que sobe os dois com um único docker compose up -d.

# Como elas se comunicam
Quando o Node gera um alerta, ele faz um pedido HTTP direto para http://localhost:5000/event. 
A Logística não conversa por HTTP; ela apenas empilha mensagens na fila logistica.urgente do RabbitMQ. 
O módulo Python fica escutando essa fila em segundo plano: assim que chega uma mensagem, ele a adiciona à sua lista de eventos. Desse modo, temos HTTP para o fluxo imediato Node → Python e RabbitMQ para o fluxo assíncrono PHP → Python.

# Onde o Redis foi usado
No serviço de Sensores, a última leitura gerada é guardada em Redis por poucos segundos; se alguém pedir /sensor-data logo em seguida, o Node devolve a cópia em cache em vez de gerar novos números. No serviço de Eventos, toda a lista de eventos é salva em Redis; se o processo reiniciar, ele recarrega essa lista e nada se perde.

# Como a fila RabbitMQ entra no fluxo
O endpoint /dispatch do PHP cria uma mensagem com o texto do despacho e publica na fila logistica.urgente. RabbitMQ armazena essa mensagem até que o consumidor Python a leia. Assim que o Python consome, ele transforma o texto em um novo objeto de evento, grava no Redis e passa a exibi-lo em /events. O uso da fila garante que o pedido urgente não dependa de a API Python estar disponível exatamente no momento em que o PHP envia a solicitação.

## 📝 Relatório do Candidato

👤 Nome Completo: Pedro Henrique Rodrigues De Sá Alcantara

Curso: Ciência da Computação

Instituição: Faculdade de Petrolina (Facape)

---

## 1️⃣ Visão Geral da Solução

O projeto é um contador de produção que não precisa ser instalado direto na máquina (não-intrusivo). Um sensor de luz (LDR) fica posicionado na esteira e detecta quando uma peça passa: a luz cai quando o objeto bloqueia o sensor, e sobe de novo quando ele passa. É nesse momento que o sistema soma +1 na contagem.

Além disso, se a esteira ficar parada tempo demais (mais de 5s com o sensor bloqueado), o sistema avisa que pode ter travado algo. Tem também um botão físico que o operador aperta pra zerar tudo no início de um novo turno.

---

## 2️⃣ Arquitetura do Sistema Embarcado

O código roda em loop, sem travar em nenhum momento (sem usar sleep/delay bloqueando o processo). Separei em duas partes que rodam paralelamente dentro do mesmo loop:

- **Leitura do LDR (a cada 100ms):** o sistema fica alternando entre dois estados, "livre" e "bloqueado". Só conta a peça quando volta de bloqueado pra livre (ou seja, quando a peça já passou por completo, não no meio do caminho). Se ficar bloqueado mais de 5 segundos direto, dispara o alerta de micro-parada, só uma vez.
- **Leitura do botão (com debounce):** compara a leitura atual com a anterior. Se mudou, espera 50ms pra confirmar que não foi só ruído. O reset só é disparado quando o botão é solto (não ao pressionar), evitando que o efeito aconteça no meio de um clique.

Fluxo resumido:

    loop principal
     |-- leitura do LDR (100ms)
     |     |-- livre -> bloqueado (lux cai)
     |     |-- bloqueado -> livre (lux sobe) -> incrementa contador
     |     `-- bloqueado por >5s -> alerta de micro-parada
     `-- leitura do botão (com debounce de 50ms)
           `-- botão solto após pressionar (estável) -> zera contadores

---

## 3️⃣ Componentes Utilizados na Simulação

- **Placa:** ESP32 DevKit C v4
- **Sensor LDR:** `wokwi-photoresistor-sensor`, id `ldr1`, ligado no GPIO34 (pino analógico). Simula a variação de luz que representa a peça passando.
- **Botão de reset:** `wokwi-pushbutton`, id `btn1`, ligado no GPIO14 com pull-up interno (quando pressionado, o pino vai pra nível baixo).
- **Serial (UART):** onde saem todas as mensagens de status, contagem e alertas.

---

## 4️⃣ Decisões Técnicas Relevantes

- Usei constantes no topo do código (`RAW_LIVRE_MAX`, `RAW_BLOQUEIO_MIN`, `LIMIAR_MICROPARADA_MS`, etc) em vez de deixar números soltos espalhados na lógica.
- Tudo é feito comparando `time.ticks_ms()` com o tempo atual, sem usar sleep. Isso é importante porque o teste automatizado do Wokwi muda os valores simulados em momentos específicos, e se o código travar em algum sleep longo, pode perder essa janela e o teste falha.
- No botão, ao invés de simplesmente ler o pino e agir na hora, fiz o debounce esperando 50ms de estabilidade antes de validar, e o reset dispara na soltura do botão (não ao pressionar), evitando problemas de timing com o teste automatizado.
- Separei a parte do LDR e a do botão em blocos diferentes dentro do loop, cada um com seu próprio controle de tempo, pra um não interferir no outro.
- O sensor LDR simulado tem resposta invertida: mais luz gera um valor bruto de leitura menor, não maior. Calibrei os limiares testando valores reais (lux=832 → leitura ~756; lux=50 → leitura ~2531) e defini os limiares no meio dessas faixas, com margem de segurança.

---

## 5️⃣ Resultados Obtidos

Testei manualmente na simulação do Wokwi, mudando os valores e observando o terminal:

- A mensagem de inicialização aparece certinho antes de qualquer leitura
- Contagem de peças funciona: variando o lux de alto pra baixo e de volta pra alto, o contador soma certo
- O alerta de micro-parada dispara depois de manter o sensor bloqueado por mais de 5s, e não fica repetindo enquanto continua bloqueado
- O reset zera os contadores com um único clique, sem disparar a mensagem mais de uma vez por clique

---

## 6️⃣ Comentários Adicionais

A parte que me deu mais trabalho foi o botão — na primeira versão, sem debounce, um clique só gerava várias mensagens de reset ao mesmo tempo. Resolvi isso esperando o valor ficar estável por 50ms antes de considerar válido, em vez de reagir na primeira leitura que muda.

Outro problema foi o momento exato em que o reset disparava: no começo, ele acontecia assim que detectava o botão pressionado, mas isso fazia a mensagem sair antes do teste automatizado terminar de simular a soltura do botão, e o teste falhava por timeout. Mudei para disparar só quando o botão é solto, o que resolveu e também é mais coerente com o funcionamento físico esperado de um botão.

Tive um problema parecido com a calibração do sensor de luz: descobri que a leitura dele é invertida — mais luz gera um valor bruto menor, não maior, o contrário do que eu esperava inicialmente. Só percebi isso testando os valores reais na simulação (lux 832 deu leitura ~756, lux 50 deu leitura ~2531) e ajustei os limiares com base nesses números.

Por fim, tive cuidado pra não usar delay em nenhum ponto do código, já que o teste automatizado altera os valores em momentos certos e um delay longo poderia fazer o firmware perder essa mudança.

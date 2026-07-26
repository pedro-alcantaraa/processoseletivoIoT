from machine import Pin, ADC
import time

ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)

btn = Pin(14, Pin.IN, Pin.PULL_UP)

# RAW alto = pouca luz (bloqueado) | RAW baixo = muita luz (livre) -- relação invertida
RAW_LIVRE_MAX = 1200     # abaixo disso = luz alta = linha livre
RAW_BLOQUEIO_MIN = 1800  # acima disso = luz baixa = peça bloqueando

LIMIAR_MICROPARADA_MS = 5000
INTERVALO_LEITURA_MS = 100
DEBOUNCE_MS = 50

ESTADO_LIVRE = "livre"
ESTADO_BLOQUEADO = "bloqueado"


def main():
    print("Contador de Producao Inicializado")

    total_pecas = 0
    estado_atual = ESTADO_LIVRE
    bloqueio_inicio_ms = None
    microparada_disparada = False

    btn_estavel = 1
    btn_ultima_leitura = 1
    btn_ultima_mudanca_ms = time.ticks_ms()

    ultima_leitura_ms = time.ticks_ms()

    while True:
        agora = time.ticks_ms()

        if time.ticks_diff(agora, ultima_leitura_ms) >= INTERVALO_LEITURA_MS:
            ultima_leitura_ms = agora
            raw = ldr.read()

            if estado_atual == ESTADO_LIVRE and raw >= RAW_BLOQUEIO_MIN:
                estado_atual = ESTADO_BLOQUEADO
                bloqueio_inicio_ms = agora
                microparada_disparada = False

            elif estado_atual == ESTADO_BLOQUEADO and raw <= RAW_LIVRE_MAX:
                total_pecas += 1
                print("Peca detectada! Total: {}".format(total_pecas))
                estado_atual = ESTADO_LIVRE
                bloqueio_inicio_ms = None
                microparada_disparada = False

            if estado_atual == ESTADO_BLOQUEADO and not microparada_disparada:
                if time.ticks_diff(agora, bloqueio_inicio_ms) >= LIMIAR_MICROPARADA_MS:
                    print("Alerta: Micro-parada detectada!")
                    microparada_disparada = True

        leitura_atual = btn.value()
        if leitura_atual != btn_ultima_leitura:
            btn_ultima_mudanca_ms = agora
            btn_ultima_leitura = leitura_atual

        if time.ticks_diff(agora, btn_ultima_mudanca_ms) >= DEBOUNCE_MS:
            if leitura_atual != btn_estavel:
                btn_estavel = leitura_atual
                if btn_estavel == 0:
                    total_pecas = 0
                    estado_atual = ESTADO_LIVRE
                    bloqueio_inicio_ms = None
                    microparada_disparada = False
                    print("Turno resetado com sucesso. Contadores zerados.")


if __name__ == "__main__":
    main()
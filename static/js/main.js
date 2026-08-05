/* ==========================================================================
   FeeSync — main.js
   Mascara de moeda, captura de formulario assincrono (Fetch API)
   e atualizacao animada dos cards de resultado.
   ========================================================================== */

(function () {
    'use strict';

    // -----------------------------------------------------------------------
    // Utilidades de formatacao
    // -----------------------------------------------------------------------

    /**
     * Formata um numero como moeda BRL (R$ 15.000,00)
     */
    function formatBRL(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL',
        }).format(value);
    }

    /**
     * Extrai valor numerico de uma string formatada como moeda.
     * "R$ 15.000,50" -> 15000.50
     */
    function parseBRL(str) {
        if (!str) return 0;
        var cleaned = str.replace(/[R$\s.]/g, '').replace(',', '.');
        var num = parseFloat(cleaned);
        return isNaN(num) ? 0 : num;
    }

    // -----------------------------------------------------------------------
    // Mascara de moeda em tempo real
    // -----------------------------------------------------------------------

    function setupCurrencyMask(inputEl) {
        inputEl.addEventListener('input', function () {
            var raw = this.value.replace(/\D/g, '');
            if (raw === '') {
                this.value = '';
                return;
            }
            var cents = parseInt(raw, 10);
            var reais = cents / 100;
            this.value = formatBRL(reais);
        });

        // Selecionar todo o texto ao focar para facilitar edicao
        inputEl.addEventListener('focus', function () {
            var self = this;
            setTimeout(function () { self.select(); }, 0);
        });
    }

    // -----------------------------------------------------------------------
    // Animacao de contagem incremental
    // -----------------------------------------------------------------------

    function animateValue(el, targetValue, duration, isCurrency) {
        if (typeof isCurrency === 'undefined') isCurrency = true;
        var start = 0;
        var startTime = null;

        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            var progress = Math.min((timestamp - startTime) / duration, 1);
            // Ease-out cubic
            var eased = 1 - Math.pow(1 - progress, 3);
            var current = eased * targetValue;

            if (isCurrency) {
                el.textContent = formatBRL(current);
            } else {
                el.textContent = current.toFixed(1);
            }

            if (progress < 1) {
                window.requestAnimationFrame(step);
            } else {
                // Valor final exato
                if (isCurrency) {
                    el.textContent = formatBRL(targetValue);
                } else {
                    el.textContent = targetValue;
                }
            }
        }

        window.requestAnimationFrame(step);
    }

    // -----------------------------------------------------------------------
    // Toast de erro
    // -----------------------------------------------------------------------

    var toastTimeout = null;

    function showToast(message) {
        var toast = document.getElementById('toast');
        if (!toast) return;
        var body = toast.querySelector('.toast__body');
        if (body) body.textContent = message;
        toast.classList.add('visible');

        if (toastTimeout) clearTimeout(toastTimeout);
        toastTimeout = setTimeout(function () {
            toast.classList.remove('visible');
        }, 5000);
    }

    // -----------------------------------------------------------------------
    // Envio do formulario
    // -----------------------------------------------------------------------

    function handleSubmit(e) {
        e.preventDefault();

        var btn = document.getElementById('submitBtn');
        var btnText = btn.querySelector('.btn-text');
        var btnSpinner = btn.querySelector('.spinner');

        // Estado de loading
        btnText.textContent = 'Calculando\u2026';
        if (btnSpinner) btnSpinner.style.display = 'block';
        btn.disabled = true;

        var custoFixoRaw = document.getElementById('custoFixo').value;
        var custoFixo = parseBRL(custoFixoRaw);

        var payload = {
            custo_fixo_mensal: custoFixo,
            horas_produtivas_mes: parseInt(document.getElementById('horasProdutivas').value, 10) || 0,
            margem_lucro_alvo: parseFloat(document.getElementById('margemLucro').value) || 0,
            nome_empresa: document.getElementById('nomeEmpresa').value.trim(),
            regime_tributario: document.getElementById('regimeTributario').value,
            ramo_atividade: document.getElementById('ramoAtividade').value,
            volume_nfe: document.getElementById('volumeNfe').value,
            num_funcionarios_socios: parseInt(document.getElementById('numFuncionarios').value, 10) || 0,
        };

        fetch('/api/calcular', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        })
        .then(function (res) {
            return res.json().then(function (data) {
                return { ok: res.ok, data: data };
            });
        })
        .then(function (result) {
            if (!result.ok) {
                showToast(result.data.error || 'Erro ao processar os dados.');
                return;
            }

            var data = result.data;

            // Mostrar painel de resultados
            var panel = document.getElementById('resultados');
            panel.classList.add('visible');

            // Animar valores
            var elPiso = document.getElementById('resPiso');
            var elRecomendado = document.getElementById('resRecomendado');
            var elMercado = document.getElementById('resMercado');
            var elHoras = document.getElementById('resHoras');

            animateValue(elPiso, data.piso_custo, 800, true);
            animateValue(elRecomendado, data.valor_recomendado, 800, true);

            // Mercado: fade-in da faixa
            elMercado.style.opacity = '0';
            setTimeout(function () {
                elMercado.textContent = formatBRL(data.mercado_min) + ' \u2013 ' + formatBRL(data.mercado_max);
                elMercado.style.transition = 'opacity 0.4s ease';
                elMercado.style.opacity = '1';
            }, 200);

            // Horas estimadas
            if (elHoras) {
                elHoras.textContent = data.horas_estimadas + 'h/mes';
            }
        })
        .catch(function () {
            showToast('Erro de conexao com o servidor.');
        })
        .finally(function () {
            btnText.textContent = 'Calcular Honorarios';
            if (btnSpinner) btnSpinner.style.display = 'none';
            btn.disabled = false;
        });
    }

    // -----------------------------------------------------------------------
    // Inicializacao
    // -----------------------------------------------------------------------

    document.addEventListener('DOMContentLoaded', function () {
        // Mascara de moeda
        var custoInput = document.getElementById('custoFixo');
        if (custoInput) setupCurrencyMask(custoInput);

        // Formulario
        var form = document.getElementById('calcForm');
        if (form) form.addEventListener('submit', handleSubmit);
    });
})();

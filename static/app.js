document.addEventListener("DOMContentLoaded", () => {
    // Lucide Icons Initialization
    lucide.createIcons();

    // DOM Elements
    const btnTabSingle = document.getElementById("btn-tab-single");
    const btnTabBatch = document.getElementById("btn-tab-batch");
    const panelSingle = document.getElementById("panel-single");
    const panelBatch = document.getElementById("panel-batch");

    const inputUrl = document.getElementById("input-url");
    const selectCountry = document.getElementById("select-country");
    const selectCountryBatch = document.getElementById("select-country-batch");
    const btnRunAnalysis = document.getElementById("btn-run-analysis");

    const dropZone = document.getElementById("drop-zone");
    const batchFileInput = document.getElementById("batch-file-input");
    const batchFileInfo = document.getElementById("batch-file-info");
    const batchFilename = document.getElementById("batch-filename");
    const batchFilesize = document.getElementById("batch-filesize");
    const btnRemoveFile = document.getElementById("btn-remove-file");
    const btnRunBatch = document.getElementById("btn-run-batch");

    const btnRefreshHistory = document.getElementById("btn-refresh-history");
    const historyItems = document.getElementById("history-items");

    const welcomeScreen = document.getElementById("welcome-screen");
    const loadingScreen = document.getElementById("loading-screen");
    const loadingText = document.getElementById("loading-text");
    const dashboardScreen = document.getElementById("dashboard-screen");
    const batchResultsScreen = document.getElementById("batch-results-screen");

    // Charts references
    let ichChartInstance = null;
    let iacChartInstance = null;
    let ivsChartInstance = null;
    let radarChartInstance = null;

    // Batch variables
    let batchUrls = [];

    // Initialize Page
    loadCountries();
    loadHistory();

    // ==========================================================================
    // TABS SYSTEM
    // ==========================================================================
    btnTabSingle.addEventListener("click", () => {
        btnTabSingle.classList.add("active");
        btnTabBatch.classList.remove("active");
        panelSingle.classList.remove("hidden");
        panelBatch.classList.add("hidden");
    });

    btnTabBatch.addEventListener("click", () => {
        btnTabBatch.classList.add("active");
        btnTabSingle.classList.remove("active");
        panelBatch.classList.remove("hidden");
        panelSingle.classList.add("hidden");
    });

    // Details tabs
    const detailsTabButtons = document.querySelectorAll(".details-tab-btn");
    detailsTabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            detailsTabButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const targetTab = btn.getAttribute("data-tab");
            document.querySelectorAll(".details-tab-content").forEach(content => {
                content.classList.remove("active");
            });
            document.getElementById(targetTab).classList.add("active");
        });
    });

    // ==========================================================================
    // API CALLS & LOADERS
    // ==========================================================================
    async function loadCountries() {
        try {
            const res = await fetch("/countries");
            const countries = await res.json();
            
            // Limpiar y popular dropdowns
            selectCountry.innerHTML = '<option value="">Detectar automáticamente</option>';
            selectCountryBatch.innerHTML = '<option value="auto">Detectar automáticamente por sitio</option>';

            countries.forEach(c => {
                const opt1 = document.createElement("option");
                opt1.value = c.code;
                opt1.textContent = `${c.name} (${c.code})`;
                selectCountry.appendChild(opt1);

                const opt2 = document.createElement("option");
                opt2.value = c.code;
                opt2.textContent = `${c.name} (${c.code})`;
                selectCountryBatch.appendChild(opt2);
            });

            // Establecer México (MEX) por defecto en lote
            selectCountryBatch.value = "MEX";
        } catch (err) {
            console.error("Error al cargar la lista de países:", err);
        }
    }

    async function loadHistory() {
        historyItems.innerHTML = '<div class="history-empty">Cargando historial...</div>';
        try {
            const res = await fetch("/history");
            const history = await res.json();

            if (history.length === 0) {
                historyItems.innerHTML = '<div class="history-empty">No hay análisis recientes.</div>';
                return;
            }

            historyItems.innerHTML = "";
            history.forEach(item => {
                const div = document.createElement("div");
                div.className = "history-item";
                
                // Formatear url corta
                let shortUrl = (item.url || "").replace("https://", "").replace("http://", "");
                if (shortUrl.length > 22) shortUrl = shortUrl.substring(0, 20) + "...";

                const dateFormated = (item.date || "").split(" ")[0]; // solo fecha YYYY-MM-DD

                div.innerHTML = `
                    <div class="history-item-header">
                        <span class="history-domain" title="${item.url}">${shortUrl}</span>
                        <span class="history-scores">IAC: ${(item.IAC * 100).toFixed(0)}</span>
                    </div>
                    <div class="history-countries">
                        <span>${item.pais_origen || "auto"}</span>
                        <i data-lucide="arrow-right" style="width: 10px; height: 10px;"></i>
                        <span style="color: var(--color-primary); font-weight: 600;">${item.pais_objetivo || "auto"}</span>
                    </div>
                    <div class="history-date">${item.date}</div>
                `;

                div.addEventListener("click", () => loadHistoryItem(item.filename));
                historyItems.appendChild(div);
            });
            lucide.createIcons();
        } catch (err) {
            historyItems.innerHTML = '<div class="history-empty text-danger">Error cargando historial</div>';
            console.error("Error al cargar el historial:", err);
        }
    }

    btnRefreshHistory.addEventListener("click", loadHistory);

    async function loadHistoryItem(filename) {
        showLoading("Cargando reporte histórico...");
        try {
            const res = await fetch(`/history/${filename}`);
            if (!res.ok) throw new Error("Error al obtener reporte");
            const data = await res.json();
            renderDashboard(data);
        } catch (err) {
            alert("No se pudo cargar el análisis histórico: " + err.message);
            showWelcome();
        }
    }

    // ==========================================================================
    // ANALYSIS RUN (SINGLE)
    // ==========================================================================
    btnRunAnalysis.addEventListener("click", async () => {
        const urlVal = inputUrl.value.trim();
        if (!urlVal) {
            alert("Por favor introduce una URL válida.");
            return;
        }

        const countryVal = selectCountry.value || null;

        showLoading("Analizando sitio web con Playwright y AI...");

        try {
            const res = await fetch("/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: urlVal, country: countryVal })
            });

            if (!res.ok) {
                const text = await res.text();
                throw new Error(text || "Error en el servidor");
            }

            const data = await res.json();
            renderDashboard(data);
            loadHistory(); // Recargar historial
        } catch (err) {
            console.error(err);
            alert("Error en el análisis:\n" + err.message);
            showWelcome();
        }
    });

    // ==========================================================================
    // BATCH UPLOAD SYSTEM (CSV)
    // ==========================================================================
    // Click en la zona abre el file input
    dropZone.addEventListener("click", () => batchFileInput.click());

    // Drag events
    ["dragenter", "dragover"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.add("drag-over");
        }, false);
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.remove("drag-over");
        }, false);
    });

    dropZone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) handleBatchFile(files[0]);
    });

    batchFileInput.addEventListener("change", (e) => {
        if (e.target.files.length) handleBatchFile(e.target.files[0]);
    });

    function handleBatchFile(file) {
        if (!file.name.endsWith(".csv")) {
            alert("El archivo seleccionado debe ser un archivo CSV.");
            return;
        }

        // Leer archivo
        const reader = new FileReader();
        reader.onload = function(e) {
            const text = e.target.result;
            parseCSVUrls(text, file.name, file.size);
        };
        reader.readAsText(file);
    }

    function parseCSVUrls(csvText, name, size) {
        const lines = csvText.split(/\r?\n/);
        if (lines.length === 0) {
            alert("El archivo CSV está vacío.");
            return;
        }

        // Buscar cabecera
        const headers = lines[0].split(",");
        const urlColIndex = headers.findIndex(h => h.trim().toLowerCase() === "url");
        
        if (urlColIndex === -1) {
            alert("El archivo CSV debe contener una columna llamada 'url' en la primera fila.");
            return;
        }

        batchUrls = [];
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line || line.startsWith("#")) continue;

            const cols = line.split(",");
            const urlVal = cols[urlColIndex] ? cols[urlColIndex].trim() : "";
            if (urlVal && !urlVal.startsWith("#")) {
                batchUrls.push(urlVal);
            }
        }

        if (batchUrls.length === 0) {
            alert("No se encontraron URLs válidas en el CSV.");
            return;
        }

        // Mostrar detalles del archivo
        batchFilename.textContent = name;
        batchFilesize.textContent = `${(size / 1024).toFixed(1)} KB (${batchUrls.length} URLs encontradas)`;
        
        dropZone.classList.add("hidden");
        batchFileInfo.classList.remove("hidden");
        btnRunBatch.disabled = false;
    }

    btnRemoveFile.addEventListener("click", () => {
        batchFileInput.value = "";
        batchUrls = [];
        dropZone.classList.remove("hidden");
        batchFileInfo.classList.add("hidden");
        btnRunBatch.disabled = true;
    });

    // RUN BATCH
    btnRunBatch.addEventListener("click", async () => {
        if (batchUrls.length === 0) return;

        const countryVal = selectCountryBatch.value;
        showLoading(`Procesando lote de ${batchUrls.length} sitios web en segundo plano...`);

        try {
            const res = await fetch("/batch-analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ urls: batchUrls, country: countryVal })
            });

            if (!res.ok) {
                const text = await res.text();
                throw new Error(text || "Error en lote");
            }

            const data = await res.json();
            renderBatchResults(data);
            loadHistory();
        } catch (err) {
            console.error(err);
            alert("Error al procesar el lote:\n" + err.message);
            showWelcome();
        }
    });

    // ==========================================================================
    // RENDERERS (DASHBOARD)
    // ==========================================================================
    function renderDashboard(data) {
        hideAllScreens();
        dashboardScreen.classList.remove("hidden");

        // Cabecera
        const evaluatedUrl = data.url || "Desconocido";
        document.getElementById("evaluated-domain").textContent = evaluatedUrl.replace("https://", "").replace("http://", "").split("/")[0];
        document.getElementById("evaluated-date").textContent = `Evaluado el: ${new Date().toLocaleDateString()} a las ${new Date().toLocaleTimeString()}`;
        
        // Banderas/Nombres de países
        const originCode = data.pais_origen || "USA";
        const targetCode = data.pais_objetivo || "MEX";
        document.getElementById("display-origin-country").textContent = `${data.pais_origen_nombre} (${originCode})`;
        document.getElementById("display-target-country").textContent = `${data.pais_objetivo_nombre} (${targetCode})`;

        // Badge de autodetcción
        const badgeElement = document.getElementById("detected-badge");
        if (data.heuristics && data.heuristics.source === "fallback") {
            badgeElement.className = "badge badge-danger";
            badgeElement.textContent = "Falló evaluación AI (Usando Fallback)";
        } else {
            badgeElement.className = "badge";
            badgeElement.textContent = `Origen: ${originCode} | Destino: ${targetCode}`;
        }

        // Renderizar los 3 Gauges
        renderRadialGauge("#chart-ich", data.ICH || 0, "ICH", ["#10b981", "#059669"]);
        renderRadialGauge("#chart-iac", data.IAC || 0, "IAC", ["#6366f1", "#4f46e5"]);
        renderRadialGauge("#chart-ivs", data.IVS || 0, "IVS", ["#0ea5e9", "#2563eb"]);

        // Renderizar Brecha
        const gapVal = data.Brecha || 0;
        const displayGap = document.getElementById("display-gap-value");
        displayGap.textContent = (gapVal >= 0 ? "+" : "") + gapVal.toFixed(3);

        const badgeGap = document.getElementById("gap-status-badge");
        if (Math.abs(gapVal) < 0.02) {
            badgeGap.className = "gap-status-badge gap-status-yellow";
            badgeGap.textContent = "Brecha Mínima";
        } else if (gapVal < 0) {
            badgeGap.className = "gap-status-badge gap-status-red";
            badgeGap.textContent = "Desajuste Cultural";
        } else {
            badgeGap.className = "gap-status-badge gap-status-green";
            badgeGap.textContent = "Alineación Positiva";
        }

        // Gráfico de Radar de Hofstede
        renderRadarHofstede(data);

        // Recomendaciones
        renderRecommendationsList(data.recomendaciones);

        // Heurísticas en Detalle
        renderHeuristicsTab(data.heuristics);

        // Visuales en Detalle
        renderVisualsTab(data.visual_analysis);

        // Re-crear iconos de lucide
        lucide.createIcons();
    }

    // Gauge RadialBar
    function renderRadialGauge(selector, val, id, gradientColors) {
        // En ApexCharts el valor va de 0 a 100
        const percentage = Math.round(val * 100);

        const options = {
            series: [percentage],
            chart: {
                height: 160,
                type: 'radialBar',
                sparkline: { enabled: true }
            },
            plotOptions: {
                radialBar: {
                    startAngle: -90,
                    endAngle: 90,
                    track: {
                        background: 'rgba(255,255,255,0.05)',
                        strokeWidth: '97%',
                        margin: 5,
                    },
                    dataLabels: {
                        name: { show: false },
                        value: {
                            offsetY: -2,
                            fontSize: '22px',
                            fontWeight: '800',
                            fontFamily: 'Outfit, sans-serif',
                            color: '#fff',
                            formatter: function (v) {
                                return v + "%";
                            }
                        }
                    }
                }
            },
            fill: {
                type: 'gradient',
                gradient: {
                    shade: 'dark',
                    type: 'horizontal',
                    gradientToColors: [gradientColors[0]],
                    stops: [0, 100],
                    colorStops: [
                        { offset: 0, color: gradientColors[0], opacity: 1 },
                        { offset: 100, color: gradientColors[1], opacity: 1 }
                    ]
                }
            },
            stroke: { lineCap: 'round' }
        };

        if (id === "ICH" && ichChartInstance) ichChartInstance.destroy();
        if (id === "IAC" && iacChartInstance) iacChartInstance.destroy();
        if (id === "IVS" && ivsChartInstance) ivsChartInstance.destroy();

        const chart = new ApexCharts(document.querySelector(selector), options);
        chart.render();

        if (id === "ICH") ichChartInstance = chart;
        if (id === "IAC") iacChartInstance = chart;
        if (id === "IVS") ivsChartInstance = chart;
    }

    // Gráfico de Radar
    function renderRadarHofstede(data) {
        const originCode = data.pais_origen || "Origen";
        const targetCode = data.pais_objetivo || "Destino";
        
        const dims = ["DP", "IND", "EI", "OLP", "LCS", "OGI"];
        const labels = [
            "Distancia Poder (DP)",
            "Individualismo (IND)",
            "Evitación Incertidumbre (EI)",
            "Largo Plazo (OLP)",
            "Laxitud / Indulgencia (LCS)",
            "Masculinidad / Feminidad (OGI)"
        ];

        const originProfile = data.pais_origen_profile || {};
        const targetProfile = data.pais_objetivo_profile || {};

        // Mapear series multiplicando por 100 para representarlo en escala 0-100
        const originSeries = dims.map(d => {
            const v = originProfile[d];
            return v !== undefined && v !== null ? Math.round(v * 100) : 0;
        });

        const targetSeries = dims.map(d => {
            const v = targetProfile[d];
            return v !== undefined && v !== null ? Math.round(v * 100) : 0;
        });

        const options = {
            series: [{
                name: data.pais_origen_nombre || originCode,
                data: originSeries
            }, {
                name: data.pais_objetivo_nombre || targetCode,
                data: targetSeries
            }],
            chart: {
                height: 420,
                type: 'radar',
                toolbar: { show: false },
                dropShadow: {
                    enabled: true,
                    blur: 8,
                    left: 1,
                    top: 1,
                    opacity: 0.2
                }
            },
            plotOptions: {
                radar: {
                    size: 120,
                    polygons: {
                        strokeColors: 'rgba(255, 255, 255, 0.08)',
                        connectorColors: 'rgba(255, 255, 255, 0.08)',
                        fill: {
                            colors: ['rgba(255, 255, 255, 0.01)', 'rgba(255, 255, 255, 0.02)']
                        }
                    }
                }
            },
            colors: ['#0ea5e9', '#6366f1'],
            stroke: { width: 2 },
            fill: { opacity: 0.15 },
            markers: { size: 4 },
            xaxis: {
                categories: labels,
                labels: {
                    style: {
                        colors: Array(6).fill('#94a3b8'),
                        fontSize: '11px',
                        fontFamily: 'Inter, sans-serif'
                    }
                }
            },
            yaxis: {
                show: false,
                min: 0,
                max: 120
            },
            legend: {
                position: 'top',
                horizontalAlign: 'center',
                labels: { colors: '#f8fafc' },
                fontFamily: 'Outfit, sans-serif'
            },
            grid: {
                borderColor: 'rgba(255, 255, 255, 0.05)',
                strokeDashArray: 2
            }
        };

        if (radarChartInstance) radarChartInstance.destroy();
        
        const chart = new ApexCharts(document.querySelector("#chart-radar"), options);
        chart.render();
        radarChartInstance = chart;
    }

    // Lista de Recomendaciones
    function renderRecommendationsList(recs) {
        const container = document.getElementById("recs-list-container");
        const summaryText = document.getElementById("recs-summary-text");

        if (!recs) {
            summaryText.textContent = "No hay recomendaciones generadas para este análisis.";
            container.innerHTML = "";
            return;
        }

        summaryText.innerHTML = `<p>${recs.resumen || "Recomendaciones prioritarias basadas en el análisis cultural y heurístico."}</p>`;

        const actions = recs.acciones_priorizadas || [];
        if (actions.length === 0) {
            container.innerHTML = '<div class="history-empty">No se requieren acciones urgentes.</div>';
            return;
        }

        container.innerHTML = "";
        actions.forEach(action => {
            const div = document.createElement("div");
            
            // Prioridad class
            let priorityClass = "priority-low";
            let priorityBadgeText = "Baja";
            const priorityLevel = action.prioridad || 3;
            
            if (priorityLevel === 1 || String(action.impacto_estimado).toLowerCase() === "alto") {
                priorityClass = "priority-high";
                priorityBadgeText = "Alta";
            } else if (priorityLevel === 2 || String(action.impacto_estimado).toLowerCase() === "medio") {
                priorityClass = "priority-medium";
                priorityBadgeText = "Media";
            }

            // Seleccionar icono basado en el área
            let iconName = "alert-circle";
            if (action.area === "visual") iconName = "palette";
            if (action.area === "cultural") iconName = "globe";
            if (action.area === "heuristica") iconName = "check-square";

            div.className = `rec-item ${priorityClass}`;
            div.innerHTML = `
                <div class="rec-badge-icon">
                    <i data-lucide="${iconName}" style="width: 14px; height: 14px;"></i>
                </div>
                <div class="rec-content">
                    <div class="rec-header">
                        <span class="rec-title">${action.hallazgo}</span>
                        <span class="rec-priority priority-badge-${priorityClass.replace("priority-", "")}">${priorityBadgeText}</span>
                    </div>
                    <p class="rec-desc">${action.recomendacion}</p>
                </div>
            `;

            container.appendChild(div);
        });

        // Quick wins si existen
        if (recs.quick_wins && recs.quick_wins.length > 0) {
            const divTitle = document.createElement("h4");
            divTitle.textContent = "Quick Wins (Mejoras Rápidas)";
            divTitle.style.fontSize = "13px";
            divTitle.style.marginTop = "16px";
            divTitle.style.marginBottom = "8px";
            divTitle.style.color = "var(--text-primary)";
            container.appendChild(divTitle);

            recs.quick_wins.forEach(win => {
                const divWin = document.createElement("div");
                divWin.className = "rec-item priority-low";
                divWin.innerHTML = `
                    <div class="rec-badge-icon" style="color: var(--color-success); background: rgba(16,185,129,0.1);">
                        <i data-lucide="zap" style="width: 14px; height: 14px;"></i>
                    </div>
                    <div class="rec-content">
                        <p class="rec-desc" style="font-weight: 500;">${win}</p>
                    </div>
                `;
                container.appendChild(divWin);
            });
        }
    }

    // Heurísticas en detalle
    function renderHeuristicsTab(heuristics) {
        const container = document.getElementById("heuristics-detailed-list");
        if (!heuristics) {
            container.innerHTML = '<div class="history-empty">No hay datos de heurísticas disponibles.</div>';
            return;
        }

        const descriptions = {
            "A_control_jerarquia": "Grado en el que el sitio soporta jerarquías claras, guías explícitas de navegación y control centralizado.",
            "B_lenguaje_modelos": "Uso de un vocabulario, modelos conceptuales y metáforas alineadas con las convenciones locales del usuario.",
            "C_cognicion_memoria": "Reducción de la carga cognitiva, legibilidad visual clara y retención de información simple para el usuario.",
            "D_eficiencia_tiempo": "Optimización del tiempo, fluidez en la consecución de tareas y atajos rápidos sin fricción.",
            "E_error_riesgo": "Prevención proactiva de errores, tolerancia en entradas de datos e instrucciones claras de recuperación."
        };

        const displayNames = {
            "A_control_jerarquia": "Control y Jerarquía",
            "B_lenguaje_modelos": "Lenguaje y Modelos",
            "C_cognicion_memoria": "Cognición y Memoria",
            "D_eficiencia_tiempo": "Eficiencia de Tiempo",
            "E_error_riesgo": "Prevención de Errores"
        };

        container.innerHTML = "";
        Object.keys(descriptions).forEach(key => {
            const val = heuristics[key] || 3; // default 3
            const percentage = (val / 5) * 100;
            const desc = descriptions[key];
            const name = displayNames[key];

            const card = document.createElement("div");
            card.className = "heuristic-item-card";
            card.innerHTML = `
                <div class="heuristic-header">
                    <span class="heuristic-name">${name}</span>
                    <span class="heuristic-score-num">${val}/5</span>
                </div>
                <div class="heuristic-bar-container">
                    <div class="heuristic-bar-fill" style="width: ${percentage}%;"></div>
                </div>
                <p class="heuristic-desc">${desc}</p>
            `;
            container.appendChild(card);
        });
    }

    // Análisis Visual en detalle
    function renderVisualsTab(visualData) {
        if (!visualData) return;

        // 1. Paleta de colores
        const paletteContainer = document.getElementById("color-palette-list");
        paletteContainer.innerHTML = "";
        const colors = (visualData.color && visualData.color.palette) || [];
        if (colors.length === 0) {
            paletteContainer.innerHTML = '<span class="text-muted">Ninguno detectado</span>';
        } else {
            colors.forEach(hex => {
                const swatch = document.createElement("div");
                swatch.className = "color-swatch-card";
                swatch.innerHTML = `
                    <div class="color-swatch-color" style="background-color: ${hex};"></div>
                    <span class="color-swatch-hex">${hex}</span>
                `;
                paletteContainer.appendChild(swatch);
            });
        }

        // 2. Tipografía
        const typo = visualData.typography || {};
        document.getElementById("typo-val-total").textContent = typo.total_headings || 0;
        const headings = typo.heading_structure || {};
        document.getElementById("h-val-h1").textContent = headings.h1 || 0;
        document.getElementById("h-val-h2").textContent = headings.h2 || 0;
        document.getElementById("h-val-h3").textContent = headings.h3 || 0;
        document.getElementById("h-val-h4").textContent = (headings.h4 || 0) + (headings.h5 || 0) + (headings.h6 || 0);

        const families = typo.font_families || [];
        document.getElementById("typo-val-families").textContent = families.length > 0 ? families.join(", ") : "Por defecto del navegador";

        // 3. Distribución / Layout
        const layout = visualData.layout || {};
        document.getElementById("layout-val-elements").textContent = layout.total_elements || 0;
        document.getElementById("layout-val-whitespace").textContent = layout.whitespace_ratio ? `${Math.round(layout.whitespace_ratio * 100)}%` : "0%";
        document.getElementById("layout-val-density").textContent = layout.visual_density ? layout.visual_density.toFixed(3) : "0.000";

        // 4. Componentes
        const comps = visualData.components || {};
        document.getElementById("comp-val-nav").textContent = (comps.navbar_count && comps.navbar_count > 0) ? "Sí" : "No";
        document.getElementById("comp-val-form").textContent = comps.form_count || 0;
        document.getElementById("comp-val-button").textContent = comps.button_count || 0;
        document.getElementById("comp-val-card").textContent = comps.card_count || 0;
    }

    // ==========================================================================
    // RENDERERS (BATCH)
    // ==========================================================================
    function renderBatchResults(data) {
        hideAllScreens();
        batchResultsScreen.classList.remove("hidden");

        document.getElementById("batch-metric-processed").textContent = data.processed;
        
        // Configurar botón de descarga
        const btnDownload = document.getElementById("btn-download-csv");
        if (data.summary_csv) {
            btnDownload.onclick = () => {
                window.location.href = `/download-summary/${data.summary_csv}`;
            };
            btnDownload.classList.remove("hidden");
        } else {
            btnDownload.classList.add("hidden");
        }

        const tableBody = document.getElementById("batch-table-body");
        tableBody.innerHTML = "";

        if (data.results.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center;" class="text-muted">Ningún sitio web fue procesado con éxito.</td></tr>`;
            return;
        }

        data.results.forEach(row => {
            const tr = document.createElement("tr");
            
            const rowUrl = row.url || "Desconocido";
            const name = rowUrl.replace("https://", "").replace("http://", "").split("/")[0];
            const gap = row.Brecha || 0;
            const gapFormated = (gap >= 0 ? "+" : "") + gap.toFixed(3);
            
            let gapClass = "text-muted";
            if (gap < -0.02) gapClass = "text-danger";
            else if (gap > 0.02) gapClass = "text-success";

            tr.innerHTML = `
                <td><strong>${name}</strong></td>
                <td>${row.pais_origen_nombre || "Desconocido"}</td>
                <td>${row.pais_objetivo_nombre || "Desconocido"}</td>
                <td>${row.ICH ? `${(row.ICH * 100).toFixed(0)}%` : "-"}</td>
                <td>${row.IAC ? `${(row.IAC * 100).toFixed(0)}%` : "-"}</td>
                <td>${row.IVS ? `${(row.IVS * 100).toFixed(0)}%` : "-"}</td>
                <td class="${gapClass}"><strong>${gapFormated}</strong></td>
            `;

            tableBody.appendChild(tr);
        });
    }

    // ==========================================================================
    // SCREEN MANAGEMENT UTILS
    // ==========================================================================
    function showLoading(text) {
        hideAllScreens();
        loadingText.textContent = text;
        loadingScreen.classList.remove("hidden");
    }

    function showWelcome() {
        hideAllScreens();
        welcomeScreen.classList.remove("hidden");
    }

    function hideAllScreens() {
        welcomeScreen.classList.add("hidden");
        loadingScreen.classList.add("hidden");
        dashboardScreen.classList.add("hidden");
        batchResultsScreen.classList.add("hidden");
    }
});

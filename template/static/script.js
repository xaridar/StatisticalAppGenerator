
let tab = 0;
let tabs = $('.tab-handle').length;
let maxTab = 0;
let firstTab = 0;
const graphs = {};

const changeTab = (tabNum) => {
    if (tabNum >= tabs) return;
    window.scrollTo(0, 0);
    try {
        const handle = $(`.tab-handle.active`);
        handle.removeClass('active');
        $(`.tab[data-tab="${handle[0].dataset.tab}"]`).removeClass('active');
    } catch {}
    const newHandle = $(`.tab-handle:nth-child(${tabNum + 1})`);
    newHandle.addClass('active');
    try {
        $(`.tab[data-tab="${newHandle[0].dataset.tab}"]`).addClass('active');
    } catch {}
    tab = tabNum;

    /* scroll to tab */
    const diff = (newHandle.offset().left + newHandle.outerWidth()) - ($('#tabHandles').offset().left + $('#tabHandles').outerWidth());
    if (diff <= 10) return;
    let sum = 0;
    let i = 0;
    while (sum < diff && firstTab < tabs - 1) {
        firstTab++;
        sum += $(`.tab-handle:nth-child(${i + 1})`).outerWidth();
        i++;
    }
    drawTabs();
}

const closeTab = (tabNum) => {
    handle = $(`.tab-handle[data-tab]:nth-child(${tabNum + 1})`)
    if (handle.hasClass('input-tab')) return;
    $(`.tab[data-tab="${handle[0].dataset.tab}"]`).remove();
    handle.remove();
    if (firstTab > 0) {
        firstTab--;
        drawTabs();
    }
    tabs--;
    if (tabNum === tab) {
        if (tab === 0) changeTab(0);
        else if (tab < tabs) changeTab(tab);
        else changeTab(tabs - 1);
    }
}

const drawTabs = () => {
    let totalWidth = 0;
    for (let i = 0; i < firstTab; i++) {
        totalWidth += $(`.tab-handle:nth-child(${i + 1})`).outerWidth();
    }
    $('.tab-handle').css('left', `-${totalWidth}px`);
}

const popTab = (data, tab) => {
    const fontColor = getComputedStyle(document.body).getPropertyValue('--font-color');
    const gridColor = getComputedStyle(document.body).getPropertyValue('--grid-color');

    // base64
    const s = data['base64-plot'].data;
    if (s !== '') {
        const b64_div = document.createElement('div');
        b64_div.classList.add('output-ctr');
        b64_div.id = `output_b64`
        const b64_h2 = document.createElement('h2');
        b64_h2.textContent = 'Plot';
        b64_div.appendChild(b64_h2);
        const b64_img = document.createElement('img');
        const b64_ctr = document.createElement('div');
        b64_ctr.appendChild(b64_img);
        $(b64_ctr).css('width', '100%');
        b64_div.appendChild(b64_ctr);
        $(b64_img).prop('src', s);
        $(b64_img).css('width', '100%');
        $(b64_img).css('margin', 'auto');
        $(b64_img).css('display', 'block');
        $(b64_img).css('max-width', '750px');
        $(b64_img).prop('alt', 'Output Plot');
        tab.append(b64_div);
    }
    
    for (const key of Object.keys(data)) {
        const element = data[key];
        const div = document.createElement('div');
        div.classList.add('output-ctr');
        div.id = `output${key}`
        switch (element.type) {
            case 'base64':
                break;
            case 'graph': {
                if (!Object.keys(graphObj).includes(key)) return;
                div.classList.add('output-graph')
                const labelsSet = new Set(element.labels);
                const datasets = [];
                for (let i = 0; i < element.columns.length; i++) {
                    const values = element.labels.map(((label, n) => ({x: label, y: element.values[i][n]})));
                    const dataset = {
                        label: element.columns[i],
                        data: values,
                        type: Array.isArray(graphObj[key].y) ? graphObj[key].y[i] : graphObj[key].y
                    };
                    datasets.push(dataset);
                }
                const h2 = document.createElement('h2');
                h2.textContent = descriptions[key];
                div.appendChild(h2);
                labels = [...labelsSet].sort((a, b) => a - b);
                const canvas = document.createElement('canvas');
                $(canvas).addClass('output-graph');
                const ctr = document.createElement('div');
                ctr.appendChild(canvas);
                $(ctr).css('width', '100%');
                $(ctr).css('height', 'max(40vh, 30vw)');
                div.appendChild(ctr);
                
                // show chart
                const ctx = canvas.getContext('2d');
                const graph = new Chart(ctx, {
                    data: {
                        labels,
                        datasets
                    },
                    options: {
                        plugins: {
                            tooltip: {
                                intersect: false,
                                position: 'nearest',
                                mode: 'index',
                                callbacks: {
                                    label: () => {
                                        return null;
                                    },
                                    title: (context) => {
                                        return `${context[0].chart.options.scales.x.title.text} = ${context[0].label}`;
                                    },
                                    beforeBody: (context) => {
                                        return context.flatMap(ctx => ([`${ctx.dataset.label} = ${ctx.formattedValue}`]));
                                    }
                                }
                            },
                            legend: {
                                display: graphObj[key].legend,
                            }
                        },
                        scales: {
                            x: {
                                title: {
                                    text: graphObj[key].x_label,
                                    display: true,
                                    color: fontColor
                                },
                                ticks: {
                                    color: fontColor
                                },
                                grid: {
                                    color: gridColor
                                }
                            },
                            y: {
                                title: {
                                    text: graphObj[key].y_label,
                                    display: true,
                                    color: fontColor
                                },
                                ticks: {
                                    color: fontColor
                                },
                                grid: {
                                    color: gridColor
                                }
                            }
                        },
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
                if (!Object.keys(graphs).includes(maxTab)) graphs[maxTab] = {};
                graphs[maxTab][key] = graph;
                break;
            }
            case 'table': {
                const h2 = document.createElement('h2');
                h2.textContent = descriptions[key];
                div.appendChild(h2);
                const ctr = $(document.createElement('div'));
                const table = $(document.createElement('table'));

                const thead = $(document.createElement('thead'));
                for (const col of element.table.columns) {
                    const th = $(document.createElement('th'));
                    th.attr('scope', 'col');
                    th.text(col);
                    thead.append(th[0]);
                }
                table.append(thead[0]);

                const tbody = $(document.createElement('tbody'));
                for (const row of element.table.data) {
                    const tr = $(document.createElement('tr'));
                    for (const ele of row) {
                        const td = $(document.createElement('td'));
                        td.text(ele);
                        tr.append(td[0]);
                    }
                    tbody.append(tr[0]);
                }
                table.append(tbody[0]);
                ctr.addClass('table-ctr');
                ctr.append(table[0]);
                div.appendChild(ctr[0]);
                break;
            }
            case 'text': {
                const h2 = document.createElement('h2');
                h2.textContent = descriptions[key];
                div.appendChild(h2);
                const pre = $(document.createElement('pre'));
                pre.text(element.text);
                div.appendChild(pre[0]);
                break;
            }
        }
        tab.append(div);
    }
}

const copyEl = (el, numCopies) => {
    if (numCopies == '') return;
    const name = $(el).children('input').attr('name');
    $(el).children('input').val('');
    if (numCopies == 0) {
        $(el).parent().parent().css('display', 'none');
        $(`.array-input-${name}:not([data-depends-on])`).remove();
        return;
    }
    $(el).parent().parent().css('display', 'initial');
    numCopies = +numCopies;
    // destroys all other copies
    $(`.array-input-${name}:not([data-depends-on])`).remove();
    for (let i = 1; i < numCopies; i++) {
        const copy = $(el).clone();
        copy.find('label').each((_, e) => $(e).attr('for', name + '_' + i));
        copy.find('label span').each((_, e) => $(e).text('Element ' + i));
        copy.find('input').each((_, e) => $(e).attr('id', name + '_' + i));
        copy.removeAttr('data-depends-on');
        copy.children('input').val('');
        $(el).parent().append(copy[0]);
    }
}

$(() => {

    Chart.defaults.font.size = '14';
    Chart.defaults.font.family = 'monospace';
    let chart;

    $(document).on('change', '.file', function() {
        
        const error = $(this).parent().parent().find('.error');
        error.removeClass('show');

        // check file
        const file = $(this).prop('files')[0];
        if (file == undefined || file.name == '' || file.type != 'text/csv') {
            // bad file
            error.text('Only .csv files are supported.');
            error.addClass('show');
            $(this).val('');
            if (chart) chart.destroy();
            $(`label[for="${$(this).prop('id')}"] p.filename`).text('');
            return;
        }

        // read CSV file contents
        const reader = new FileReader();
        reader.onload = (e) => {
            const csv = e.target.result;
            const converted = $.csv.toObjects(csv);
            const labels = converted.map(arr => arr[this.dataset.xLabel]);
            const values = converted.map(arr => arr[this.dataset.yLabel]);
            if (labels[0] === undefined || values[0] === undefined) {
                // bad file
                error.text(`Input file does not have required x and y columns: '${this.dataset.xLabel}', '${this.dataset.yLabel}'.`);
                error.addClass('show');
                $(this).val('');
                if (chart) chart.destroy();
                $(`label[for="${$(this).prop('id')}"] p.filename`).text('');
                return;
            }
            $(`label[for="${$(this).prop('id')}"] p.filename`).text(file.name);
            // replace canvas
            if (!$(this).siblings('.filechart').length) return;

            $(this).siblings('.filechart').remove();
            const canvas = document.createElement('canvas');
            $(canvas).addClass('filechart');
            $(this).parent().append(canvas);
            
            // show chart
            const ctx = canvas.getContext('2d');
            const fontColor = getComputedStyle(document.body).getPropertyValue('--font-color');
            const gridColor = getComputedStyle(document.body).getPropertyValue('--grid-color');
            const activeColor = `rgb(${getComputedStyle(document.body).getPropertyValue('--active-color')})`;
            chart = new Chart(ctx, {
                type: 'scatter',
                data: {
                    labels,
                    datasets: [
                        {
                            data: values,
                            borderColor: activeColor,
                            backgroundColor: activeColor
                        }
                    ]
                },
                options: {
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            enabled: false
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                text: this.dataset.xLabel,
                                display: true,
                                color: fontColor
                            },
                            ticks: {
                                color: fontColor
                            },
                            grid: {
                                color: gridColor
                            }
                        },
                        y: {
                            title: {
                                text: this.dataset.yLabel,
                                display: true,
                                color: fontColor
                            },
                            ticks: {
                                color: fontColor
                            },
                            grid: {
                                color: gridColor
                            }
                        }
                    },
                    responsive: true
                }
            });
        }
        reader.readAsText(file);
    });

    $(document).on('submit', '.calcForm', async function (e) {
        e.preventDefault();
        const missing = $(this).find('.required').filter((i, el) => {
            if (!el.offsetParent) return false;
            return !$(el).val() || $(el).val() == "";
        });
        if (missing.length) {
            $('#error').text('Please fill all required fields.')
            $('#error').addClass('show');
            $(missing).addClass('missing');
            return;
        }
        $('#error').removeClass('show');
        const data = new FormData(this);
        for (const e of data.entries()) {
            if (e[1] == '') data.delete(e[0]);
        }
        $(this).find('input, button, select').prop('disabled', true);
        $(this).find('.file-upload').toggleClass('disabled', true);
        const method = $(this).attr('method');
        const action = $(this).attr('action');
        
        try {
            const res = await $.ajax(action, {
                method,
                data,
                contentType: false,
                processData: false,
            });
            if (res.success) {
                maxTab++;
                const newTab = $(document.createElement('div'));
                newTab.addClass('tab');
                newTab.attr('data-tab', tabs);
                const h1 = $(document.createElement('h1'));
                h1.text($('.tab[data-tab="0"] h1').text());
                newTab.append(h1[0]);
                const div = $(document.createElement('div'));
                div.addClass('output');
                newTab.append(div[0]);
                popTab(res.data, div);
                const download = $(document.createElement('a'));
                download.prop('href', 'javascript:print()');
                download.addClass('download-btn');
                download.text('Download output');
                download.css('display', 'inline-block');
                download.css('margin-top', '1rem');
                newTab.append(download[0]);
                $('#tabs').append(newTab[0]);
                
                const handle = $((document).createElement('span'));
                handle.addClass('tab-handle');
                handle.text(`Output ${maxTab}`);
                handle.attr('draggable', 'true');
                handle.attr('data-tab', tabs);
                const close = $((document).createElement('i'));
                close.addClass('material-icons close');
                close.text('close');
                handle.append(close[0]);
                $('#tabHandles').append(handle[0]);

                tabs++;
                changeTab(tabs-1);
            } else {
                $('#error').text(res.error)
                $('#error').addClass('show');
            }
        } catch (e) {
            console.error(e);
        }
        $(this).find('input, button, select').prop('disabled', false);
        $(this).find('.file-upload').toggleClass('disabled', false);
    });

    $(document).on('click', '.tab-handle', function(e) {
        changeTab($(e.target).index());
    });

    $(document).on('click', '.tab-handle .close', function(e) {
        closeTab($(e.target).parent().index());
        e.stopPropagation();
    });

    /* Tab dragging */
 
    $('#handlesCtr').on("dragstart", function(e) {
        $(e.target).addClass('dragging');
    });
     
    $('#tabHandles').on("dragend", function(e) {
        $(e.target).removeClass('dragging');
    });

    $('#tabHandles').on("dragover", function(e) {
        e.preventDefault();
        el = $('#tabHandles .dragging').detach()[0]
        const afterElement = getDragAfterElement($('#tabHandles'), e.clientX);
        if (!afterElement) {
            $('#tabHandles').append(el);
        } else {
            $('#tabHandles')[0].insertBefore(el, afterElement);
        }
    });

    let canShift = true;

    $('#tabsLeft').on("dragover", function (e) {
        e.preventDefault();
        if (!canShift) return;
        canShift = false;
        if (firstTab > 0) firstTab--;
        drawTabs();
        setTimeout(() => {
            canShift = true;
        }, 600);
    });
    $('#tabsRight').on("dragover", function (e) {
        e.preventDefault();
        if (!canShift) return;
        canShift = false;
        if (firstTab < tabs - 1) firstTab++;
        drawTabs();
        setTimeout(() => {
            canShift = true;
        }, 600);
    });
    $('.moreTabs').on("dragleave", function (e) {
        e.preventDefault();
        canShift = true;
    });
     
    const getDragAfterElement = (ctr, x) => {
        const draggableElements = [...ctr.children()];
     
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = x - box.left - 2 * box.width / 3;
            if (offset < 0 && offset > closest.offset) {
                return {
                    offset: offset,
                    element: child,
                };
            } else {
                return closest;
            }
        }, {
            offset: Number.NEGATIVE_INFINITY,
        }).element;
    };
    
    /* Tab overflow */

    $('#tabsLeft').on('click', () => {
        if (firstTab > 0) firstTab--;
        drawTabs();
    });
    
    $('#tabsRight').on('click', () => {
        if (firstTab < tabs - 1) firstTab++;
        drawTabs();
    });

    /* Dependent enumeration */
    $(document).on('change', 'input[type="number"][step=1]', function () {
        const depEls = $(`[data-depends-on="${$(this).attr('name')}"]`);
        depEls.each((i, el) => {
            copyEl(el, $(this).val());
        });
    })

    $('[data-depends-on]').parent().parent().css('display', 'none');

    $(document).on('keydown', '.calcForm input.missing', function () {
        $(this).removeClass('missing');
    });
    
    /* Chart download */
    $(window).bind('beforeprint', () => {
        for (let id in Chart.instances) {
            Chart.instances[id].resize(800, 400);
        }
    });

    $(window).bind('afterprint', () => {
        for (let id in Chart.instances) {
            Chart.instances[id].resize();
        }
    });
});
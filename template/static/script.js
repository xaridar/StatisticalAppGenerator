
let tab = 0;
let tabs = $('.tab-handle').length;
let maxTab = 0;
let firstTab = 0;

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
    console.log(diff);
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

const escapeHtml = unsafe => {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
 }

const popTab = (data, tab) => {
    for (const key of Object.keys(data)) {
        const element = data[key];
        const h2 = $(document.createElement('h2'));
        h2.text(key);
        tab.append(h2);
        switch (element.type) {
            case 'graph':
                break;
            case 'table':
                const table = $(document.createElement('table'));

                const thead = $(document.createElement('thead'));
                for (const col of element.table.columns) {
                    const th = $(document.createElement('th'));
                    th.attr('scope', 'col');
                    th.text(escapeHtml(col));
                    thead.append(th[0]);
                }
                table.append(thead[0]);

                const tbody = $(document.createElement('tbody'));
                for (const row of element.table.data) {
                    const tr = $(document.createElement('tr'));
                    for (const ele of row) {
                        const td = $(document.createElement('td'));
                        td.text(escapeHtml(ele));
                        tr.append(td[0]);
                    }
                    tbody.append(tr[0]);
                }
                table.append(tbody[0]);
                tab.append(table[0]);
                break;
            case 'text':

                const pre = $(document.createElement('pre'));
                pre.text(escapeHtml(element.text));
                tab.append(pre[0]);
                break;
        }
    }
}

$(() => {

    Chart.defaults.font.size = '14';
    Chart.defaults.font.family = 'monospace';
    let chart;

    $(document).on('change', '.file', function() {

        // check file
        const file = $(this).prop('files')[0];
        if (file == undefined || file.name == '' || file.type != 'text/csv') {
            // bad file
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
                    responsive: false,
                }
            });
        }
        reader.readAsText(file);
    });

    $(document).on('submit', '.calcForm', async function (e) {
        e.preventDefault();
        if ($(this).find('.required').is((i, el) => {
            return !$(el).val() || $(el).val() == "";
        })) return;
        const data = new FormData(this);
        $(this).find('input, button, select').prop('disabled', true);
        const method = $(this).attr('method');
        const action = $(this).attr('action');
        
        const res = await $.ajax(action, {
            method,
            data,
            contentType: false,
            processData: false,
        });
        console.log(res);
        if (res.success) {
            maxTab++;
            const newTab = $(document.createElement('div'));
            newTab.addClass('tab');
            newTab.attr('data-tab', tabs);
            h1 = $(document.createElement('h1'));
            h1.text($('h1').text());
            newTab.append(h1[0]);
            popTab(res.data, newTab);
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
        }
        $(this).find('input, button, select').prop('disabled', false);
    });

    $(document).on('click', '.tab-handle', function(e) {
        console.log($(e.target).index())
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
            console.log(afterElement);
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
});
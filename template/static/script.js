let tab = 0;
let tabs = $('.tab-handle').length;
let maxTab = 0;
let firstTab = 0;

const changeTab = (tabNum) => {
    if (tabNum >= tabs) return;
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
    if (diff < 0) return;
    let sum = 0;
    let i = 0;
    while (sum < diff && firstTab < tabs - 1) {
        firstTab++;
        sum += $(`.tab-handle:nth-child(${i + 1})`).outerWidth();
        i++;
    }
}

const closeTab = (tabNum) => {
    handle = $(`.tab-handle[data-tab]:nth-child(${tabNum + 1})`)
    if (handle.hasClass('input-tab')) return;
    $(`.tab[data-tab="${handle[0].dataset.tab}"]`).remove();
    handle.remove();
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

$(() => {
    $(document).on('change', '.file', function() {

        // check file
        const file = $(this).prop('files')[0];
        if (file == undefined || file.name == '' || file.type != 'text/csv') {
            // bad file
            $(this).val('');
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
                return;
            }
            // replace canvas
            if (!$(this).siblings('.filechart').length) return;

            $(this).siblings('.filechart').remove();
            const canvas = document.createElement('canvas');
            $(canvas).addClass('filechart');
            $(this).parent().append(canvas);
            
            // show chart    
            const ctx = canvas.getContext('2d');
            const chart = new Chart(ctx, {
                type: 'scatter',
                data: {
                    labels,
                    datasets: [
                        {
                            data: values,
                        }
                    ]
                },
                options: {
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                text: this.dataset.xLabel,
                                display: true,
                            }
                        },
                        y: {
                            title: {
                                text: this.dataset.yLabel,
                                display: true,
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
            const pre = document.createElement('pre');
            pre.textContent = res.data;
            newTab.append(pre);
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
        const inner = $('.tab-handle:last-child').offset().left + $('.tab-handle:last-child').outerWidth();
        const outer = $('#tabHandles').offset().left + $('#tabHandles').outerWidth();
        if (inner > outer + 0.05 && firstTab < tabs - 1) firstTab++;
        drawTabs();
    });
});
let tab = 0;
let tabs = 1;
let maxTab = 0;

const changeTab = (tabNum) => {
    if (tabNum >= tabs) return;
    $(`[data-tab="${tab}"]`).removeClass('active');
    $(`[data-tab="${tabNum}"]`).addClass('active');
    tab = tabNum;
}

const closeTab = (tabNum) => {
    if (tabNum === 0) return;
    $(`[data-tab="${tabNum}"]`).remove();
    $('[data-tab]').each((i, el) => {
        if (el.dataset.tab > tabNum) el.dataset.tab--;
    });
    tabs--;
    if (tabNum === tab) {
        if (tab < tabs) changeTab(tab);
        else changeTab(tab - 1);
    }
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
            handle.attr('data-tab', tabs);
            handle.addClass('tab-handle');
            handle.text(`Output ${maxTab}`);
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

    $(document).on('click', '.tab-handle', function() {
        changeTab(+this.dataset.tab);
    });

    $(document).on('click', '.tab-handle .close', function(e) {
        closeTab(+this.parentElement.dataset.tab);
        e.stopPropagation();
    });
});
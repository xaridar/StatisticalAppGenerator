let tab = 0;

const changeTab = (tabNum) => {
    tab = tabNum;
    $('.tab').addClass('hidden');
    $(`.tab:nth-child(${tabNum + 1})`).removeClass('hidden');
}

$(() => {
    $(document).on('change', '.file', function() {
        // replace canvas
        $(this).siblings('.filechart').remove();
        const canvas = document.createElement('canvas');
        $(canvas).addClass('filechart');
        $(this).parent().append(canvas);

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
        const method = $(this).attr('method');
        const action = $(this).attr('action');
        const data = new FormData(this);
        
        const res = await $.ajax(action, {
            method,
            data,
            contentType: false,
            processData: false,
        });
        console.log(res);
        if (res.success) {
            const newTab = $(document.createElement('div'));
            newTab.addClass('tab');
            const pre = document.createElement('pre');
            pre.textContent = res.data;
            newTab.append(pre);
            $('#tabs').append(newTab[0]);
            changeTab(newTab.index());
        }
    });

    $(document).on('click', '.tab-handle', function () {
        changeTab($(this).parent('.tab').index());
    });
});
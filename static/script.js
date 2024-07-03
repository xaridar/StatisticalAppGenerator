$(() => {
    $(document).on('change', '.file', function() {
        // replace canvas
        $(this).siblings('.filechart').remove();
        const canvas = document.createElement('canvas');
        $(canvas).addClass('filechart');
        $(this).parent().append(canvas);

        // check file
        const file = $(this).prop('files')[0];
        if (file == undefined || file.name == '' || file.type != 'text/csv') return;

        // read CSV file contents
        const reader = new FileReader();
        reader.onload = (e) => {
            const csv = e.target.result;
            const converted = $.csv.toObjects(csv);
            const labels = converted.map(arr => arr.group);
            const values = converted.map(arr => arr.y);
            
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
                                text: 'group',
                                display: true,
                            }
                        },
                        y: {
                            title: {
                                text: 'y',
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
        if (res.success) $(this).siblings('#output').text(res.data);
        else $(this).siblings('#output').text('');
    });
});
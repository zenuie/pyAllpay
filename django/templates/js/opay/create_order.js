function create_order() {
    let amount = document.getElementById('amount').value
    let sponsor = document.getElementById('sponsor').value
    let message = document.getElementById('message').value
    if (amount > 10) {
        $.ajax({
            type: 'POST',
            url: 'http://localhost:8000/opay/',
            data: {
                'amount': amount,
                'sponsor': sponsor,
                'message': message,
            },
            success: (res) => {
                datas = res['data']
                html = ""
                for (let i in datas) {
                    html += "<input type=hidden "
                    html += "name=" + i;
                    html += " value=" + '"' + datas[i] + '"';
                    html += " >\n"
                }
                const content = document.getElementById('sendData')
                content.innerHTML = html
                console.log(html)
                content.submit()
            },
        })
    } else if (amount < 10) {
        alert("歐付寶最低金額10元喔")
    }
}
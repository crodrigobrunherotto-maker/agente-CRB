content = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cadastro</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; max-width: 300px; padding: 8px; box-sizing: border-box; }
        button { padding: 10px 20px; background-color: #007bff; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h2>Cadastro</h2>
    <form action="" method="POST">
        <div class="form-group">
            <label for="codigo">Código:</label>
            <input type="text" id="codigo" name="codigo" required>
        </div>
        <div class="form-group">
            <label for="nome">Nome:</label>
            <input type="text" id="nome" name="nome" required>
        </div>
        <div class="form-group">
            <label for="data_nascimento">Data de Nascimento:</label>
            <input type="text" id="data_nascimento" name="data_nascimento" placeholder="DD/MM/AAAA" maxlength="10" required>
        </div>
        <div class="form-group">
            <label for="email">E-mail:</label>
            <input type="email" id="email" name="email" required>
        </div>
        <button type="submit">Salvar</button>
    </form>

    <script>
        const dataInput = document.getElementById('data_nascimento');
        dataInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '').slice(0, 8);
            if (value.length >= 5) {
                e.target.value = value.replace(/(\d{2})(\d{2})(\d{1,4})/, '$1/$2/$3');
            } else if (value.length >= 3) {
                e.target.value = value.replace(/(\d{2})(\d{1,2})/, '$1/$2');
            } else {
                e.target.value = value;
            }
        });
    </script>
</body>
</html>
"""

with open("cadastro.html", "w", encoding="utf-8") as f:
    f.write(content)
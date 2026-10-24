def calcular_ocupacao_pallet(dim_pallet, dim_caixa, qtd_caixas):
    lp, ap, hp = dim_pallet
    lc, ac, hc = dim_caixa
    vol_caixa_total = (lc * ac * hc) * qtd_caixas
    vol_pallet = lp * ap * hp
    if vol_pallet == 0:
        return 0.0
    porcentagem = (vol_caixa_total / vol_pallet) * 100
    return round(porcentagem, 2)
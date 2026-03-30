# Créé par clems, le 28/03/2026 en Python 3.7

import streamlit as st

def calculer_tarif():
    st.title("Calculateur de Séjour Solidaire 🏡")
    st.subheader("Déterminez le tarif de votre séjour avec les réductions appliquées")

    # --- ENTRÉES UTILISATEUR ---
    with st.sidebar:
        st.header("Paramètres du séjour")
        saison = st.selectbox("Saison", ["Été", "Intersaison", "Hiver"])
        nuits = st.number_input("Nombre de nuits", min_value=1, value=1)
        adultes = st.number_input("Nombre d'adultes payants", min_value=1, value=1)

        st.divider()
        st.header("Options et Réductions")
        etage_milieu = st.checkbox("Logement à l'étage du milieu")
        nb_personnes_etage = 0
        if etage_milieu:
            nb_personnes_etage = st.number_input("Nombre de personnes à cet étage", min_value=1, value=1)

        plusieurs_familles = st.checkbox("réunion familiale (on se retrouve entre cousins, frère et soeur ...ect)")

        st.divider()
        st.header("Services Rendus (ménage saisonier, jardinage,travaux...) ou autre contribution en nature")
        demi_journees = st.number_input("Nombre de demi-journées de service (1 j = 1 nuit offerte/pers)", min_value=0, value=0)

    # --- LOGIQUE DE CALCUL ---

    # 1. Tarif de base
    tarifs_base = {"Été": 10, "Intersaison": 15, "Hiver": 20}
    prix_unitaire = tarifs_base[saison]

    # Total de nuitées "théoriques" pour les adultes
    total_nuitees_base = adultes * nuits

    # 2. Gestion des services (Nuits offertes)
    # Chaque demi-journée retire une unité "adulte/nuit"
    nuitees_offertes = min(demi_journees, total_nuitees_base)
    nuitees_facturables = total_nuitees_base - nuitees_offertes

    sous_total = nuitees_facturables * prix_unitaire
    explications = [f"Tarif de base ({saison}) : {prix_unitaire}€ / nuit / adulte"]
    if nuitees_offertes > 0:
        explications.append(f"Services rendus : {nuitees_offertes} nuitées offertes (économie de {nuitees_offertes * prix_unitaire}€)")

    # 3. Réductions cumulables
    reduction_totale = 0

    # Réduction étage du milieu (-15% si > 6 pers)
    if etage_milieu and nb_personnes_etage > 6:
        reduction_totale += 0.15
        explications.append("Réduction Étage du milieu (> 6 pers) : -15%")

    # Réduction Groupe
    if plusieurs_familles:
        reduction_totale += 0.10
        explications.append("Réduction Multi-familles : -10%")

    # Réduction Durée Standard (>= 7 jours)
    if nuits >= 7 and nuits <= 15:
        reduction_totale += 0.10
        explications.append("Réduction Séjour long (>= 7 jours) : -10%")

    # Application des réductions cumulables
    prix_apres_reduc = sous_total * (1 - reduction_totale)

    # 4. Réductions TRÈS Long séjour (Remplacent les précédentes si applicables)
    reduc_longue = 0
    if nuits > 30 and saison == "Été":
        reduc_longue = 0.40
        prix_apres_reduc = sous_total * (1 - reduc_longue)
        explications.append("Réduction Très Long Séjour (> 1 mois en Été) : -40% (remplace les autres réducs)")
    elif nuits > 15:
        reduc_longue = 0.20
        prix_apres_reduc = sous_total * (1 - reduc_longue)
        explications.append("Réduction Très Long Séjour (> 15 jours) : -20% (remplace les autres réducs)")

    # --- AFFICHAGE DES RÉSULTATS ---
    st.write("---")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total à payer (Adultes)", f"{max(0.0, prix_apres_reduc):.2f} €")

    with col2:
        participation = st.text_input("Participation libre (Enfants/Étudiants/Précarité)", "0")
        try:
            total_final = prix_apres_reduc + float(participation)
        except:
            total_final = prix_apres_reduc

    st.subheader("Détails du calcul :")
    for item in explications:
        st.write(f"✅ {item}")

    if total_final > 0:
        st.success(f"**Montant final total : {total_final:.2f} €**")

if __name__ == "__main__":
    calculer_tarif()

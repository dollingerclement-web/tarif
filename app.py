# Créé par clems, le 28/03/2026 en Python 3.7
import streamlit as st
def calculer_reduction_long_sejour(nuits, saison):
    """
    Calcule la réduction pour les longs séjours.
    La réduction augmente avec le nombre de nuits (croissance du prix total).
    """
    if saison == "Hiver":
        return 0  # Pas de réduction en hiver
    
    if nuits <= 15:
        return 0  # Pas de réduction pour séjours courts
    
    # Réductions progressives et continues
    if nuits <= 22:
        # Entre 15 et 22 nuits : progression linéaire de 0% à 20%
        reduction = 0.20 * (nuits - 15) / 7
    elif nuits <= 30:
        # Entre 22 et 30 nuits : progression de 20% à 35%
        reduction = 0.20 + 0.15 * (nuits - 22) / 8
    else:
        # Au-delà de 30 nuits : 40% fixe
        reduction = 0.40
    
    return reduction

def calculer_tarif():
    st.set_page_config(page_title="Calculateur Chirouze", page_icon="🏡", layout="wide")
    st.title("Calculateur de Séjour Chirouze 🏡")
    st.subheader("Déterminez le montant de votre participation aux frais")
    st.info("La chirouze est une maison familiale qui fonctionne grâce à la participation de ses usagers;nous vous remercions pour votre contribution. Vous pouvez effectuer un virement en utilisant l'IBAN suivant : ...")

    # --- ENTRÉES UTILISATEUR ---
    with st.sidebar:
        st.header("Paramètres du séjour")
        saison = st.selectbox("Saison", ["Été", "Intersaison", "Hiver"])
        nuits = st.number_input("Nombre de nuits", min_value=1, value=1)
        st.info("  Le tarif adulte actif a été calculé pour garantir le bon fonctionnement de la chirouze.  Pour les enfants ou les étudiants/adultes qui en resentent le besoin nous proposons un tarif libre. ")
        adultes = st.number_input("Nombre d'adultes actifs payants", min_value=0, value=0)
        enfant = st.number_input("Nombre d'enfants (ou adultes en tarif libre))", min_value=0, value=0)
        
       
        try:
            choix_du_prix = float(st.text_input("Participation libre/ nuit/personne", "0"))
        except ValueError:
            choix_du_prix = 0.0
        

        st.divider()
        st.header("Options et Réductions")
        etage_milieu = st.checkbox("Logement à l'étage du milieu")
        nb_personnes_etage = 0
        if etage_milieu:
            nb_personnes_etage = st.number_input("Nombre de personnes à cet étage", min_value=1, value=1)

        plusieurs_familles = st.checkbox("Réunion familiale (on se retrouve entre cousins, frère et sœur...etc)")

        st.divider()
        st.header("Services Rendus")
        st.caption("Ménage saisonnier, jardinage, travaux... ou autre contribution en nature")
        demi_journees = st.number_input("Nombre de demi-journées de service (1 j = 1 nuit offerte/pers)", min_value=0, value=0)

    # --- LOGIQUE DE CALCUL ---

    # 1. Tarif de base
    tarifs_base = {"Été": 10, "Intersaison": 15, "Hiver": 20}
    prix_unitaire = tarifs_base[saison]
    
    # Total de nuitées "théoriques" pour les adultes
    total_nuitees_base = adultes * nuits
    détail_du_calcul=str(adultes) +" *" +str(nuits)

    # 2. Gestion des services (Nuits offertes)
    nuitees_offertes = min(demi_journees, total_nuitees_base)
    nuitees_facturables = max(0, total_nuitees_base - nuitees_offertes)
    
    sous_total = nuitees_facturables * prix_unitaire
    explications = [f"Tarif de base ({saison}) : {prix_unitaire}€ / nuit / adulte"]
    if nuitees_offertes > 0:
        explications.append(f"Services rendus : {nuitees_offertes} nuitées offertes (économie de {nuitees_offertes * prix_unitaire}€)")
        détail_du_calcul=str(prix_unitaire)+"* (" +détail_du_calcul + "-"+str(nuitees_offertes)+")"

    # 3. Calcul des réductions
    reduction_totale = 1

    # Réduction étage du milieu (-15% si > 5 pers et pas Été)
    if etage_milieu and nb_personnes_etage > 5 and saison != "Été":
        reduction_totale =  reduction_totale*0.85
        explications.append("Réduction Étage du milieu (> 5 pers) : -15%")
        détail_du_calcul=str(0.85) + "* (" +détail_du_calcul + ")"
      

    # Réduction Multi-familles
    if plusieurs_familles:
        reduction_totale =reduction_totale*0.9
        explications.append("Réduction Multi-familles : -10%")
        détail_du_calcul=str(0.9) + "* (" +détail_du_calcul + ")"
    
    # Réduction Durée Standard (7 à 15 jours)
    if 7 <= nuits <= 15:
        reduction_totale =reduction_totale*0.9
        explications.append("Réduction Séjour long (7-15 jours) : -10%")
        détail_du_calcul=str(0.9) + "* (" +détail_du_calcul + ")"

    # 4. Appliquer les réductions cumulables
    prix_apres_reduc = sous_total *  reduction_totale

    #5.Application des réductions long séjour remplace les réductions cumulables
    reduction_long_sejour = calculer_reduction_long_sejour(nuits, saison)
    if reduction_long_sejour > 0:
        prix_apres_reduc = sous_total * (1 - reduction_long_sejour)
        explications = [explications[0]]  # Garder le tarif de base
        explications.append(f"Réduction Long Séjour : -{reduction_long_sejour*100:.2f}% (remplace les autres)")
         
    # 6. Application des plafonds
    prix_par_jour = prix_apres_reduc / nuits if nuits > 0 else 0
    
    if prix_par_jour > 160:
        prix_apres_reduc = 160 * nuits
        explications.append(f"Plafond groupe appliqué : 160€ / jour")
    
    if 7 <= nuits <= 15 and prix_apres_reduc > 900:
        prix_apres_reduc = 900/7*nuits
        explications.append(f"Plafond semaine appliqué : 900€ maximum")

    if 15 <= nuits <= 30 and prix_apres_reduc > 700 and adultes <3 :
        prix_apres_reduc = 700
        explications.append(f"Plafond semaine appliqué : 900€ maximum")
        
    if nuits > 30 and prix_apres_reduc > 600 and adultes <3 :
        prix_apres_reduc = 700/30*nuits
        explications.append(f"Plafond semaine appliqué : 900€ maximum")

    # calcul de la participation libre
    participation_libre = nuits * enfant * choix_du_prix
        

    # --- AFFICHAGE DES RÉSULTATS ---
    st.write("---")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Tarif calculé (Adultes)", f"{max(0.0, prix_apres_reduc):.2f} €")

    with col2:
        st.metric("Participation libre (Enfants/Étudiants/ect)", f"{max(0.0, participation_libre):.2f} €")

        total_final = max(0.0, prix_apres_reduc + participation_libre)

    st.subheader("Détails du calcul :")
    for item in explications:
        st.write(f"✅ {item}")
    st.caption(détail_du_calcul)
    st.divider()
    st.success(f"### Montant final total : **{total_final:.2f} €**")

if __name__ == "__main__":
    calculer_tarif()

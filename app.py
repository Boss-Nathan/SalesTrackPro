import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import date

# ─────────────────────────────────────────
# CONFIG DE LA PAGE
# ─────────────────────────────────────────
st.set_page_config(
    page_title="SalesTrack Pro",
    page_icon="🛒",
    layout="wide"
)

# ─────────────────────────────────────────
# FICHIER DE STOCKAGE
# ─────────────────────────────────────────
DATA_FILE = "ventes.csv"

def charger_donnees():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Date", "Produit", "Categorie", "Quantite", "Prix_Unitaire", "Vendeur"])

def sauvegarder_donnees(df):
    df.to_csv(DATA_FILE, index=False)

# ─────────────────────────────────────────
# TITRE
# ─────────────────────────────────────────
st.title("🛒 SalesTrack Pro")
st.markdown("### Application de collecte et d'analyse des ventes")
st.divider()

# ─────────────────────────────────────────
# MENU LATERAL
# ─────────────────────────────────────────
menu = st.sidebar.radio("📌 Navigation", [
    "➕ Enregistrer une vente",
    "📋 Voir les données",
    "📊 Analyse & Statistiques",
    "📈 Graphiques"
])

df = charger_donnees()

# ═══════════════════════════════════════════
# PAGE 1 : FORMULAIRE DE SAISIE
# ═══════════════════════════════════════════
if menu == "➕ Enregistrer une vente":
    st.header("➕ Enregistrer une nouvelle vente")

    col1, col2 = st.columns(2)

    with col1:
        date_vente = st.date_input("📅 Date de la vente", value=date.today())
        produit = st.text_input("🏷️ Nom du produit", placeholder="Ex: Téléphone Samsung")
        categorie = st.selectbox("📦 Catégorie", [
            "Électronique", "Alimentation", "Vêtements",
            "Mobilier", "Cosmétiques", "Autres"
        ])

    with col2:
        quantite = st.number_input("🔢 Quantité vendue", min_value=1, step=1)
        prix = st.number_input("💰 Prix unitaire (FCFA)", min_value=0.0, step=100.0)
        vendeur = st.text_input("👤 Nom du vendeur", placeholder="Ex: Jean Dupont")

    total = quantite * prix
    st.info(f"💵 **Total de cette vente : {total:,.0f} FCFA**")

    if st.button("✅ Enregistrer la vente", use_container_width=True):
        if produit == "" or vendeur == "":
            st.error("⚠️ Veuillez remplir tous les champs !")
        else:
            nouvelle_vente = {
                "Date": str(date_vente),
                "Produit": produit,
                "Categorie": categorie,
                "Quantite": quantite,
                "Prix_Unitaire": prix,
                "Vendeur": vendeur
            }
            df = pd.concat([df, pd.DataFrame([nouvelle_vente])], ignore_index=True)
            sauvegarder_donnees(df)
            st.success(f"✅ Vente enregistrée avec succès ! Total : {total:,.0f} FCFA")
            st.balloons()

# ═══════════════════════════════════════════
# PAGE 2 : TABLEAU DES DONNÉES
# ═══════════════════════════════════════════
elif menu == "📋 Voir les données":
    st.header("📋 Toutes les ventes enregistrées")

    if df.empty:
        st.warning("⚠️ Aucune vente enregistrée pour l'instant.")
    else:
        df["Total"] = df["Quantite"] * df["Prix_Unitaire"]
        st.dataframe(df, use_container_width=True)
        st.success(f"✅ {len(df)} vente(s) enregistrée(s) au total")

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Télécharger les données (CSV)",
            data=csv,
            file_name="ventes_export.csv",
            mime="text/csv"
        )

# ═══════════════════════════════════════════
# PAGE 3 : STATISTIQUES
# ═══════════════════════════════════════════
elif menu == "📊 Analyse & Statistiques":
    st.header("📊 Analyse descriptive des ventes")

    if df.empty:
        st.warning("⚠️ Aucune donnée disponible. Enregistrez d'abord des ventes.")
    else:
        df["Total"] = df["Quantite"] * df["Prix_Unitaire"]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Chiffre d'affaires total", f"{df['Total'].sum():,.0f} FCFA")
        col2.metric("📦 Nombre de ventes", len(df))
        col3.metric("📈 Vente moyenne", f"{df['Total'].mean():,.0f} FCFA")
        col4.metric("🏆 Vente max", f"{df['Total'].max():,.0f} FCFA")

        st.divider()
        st.subheader("🏷️ Statistiques par produit")
        stats = df.groupby("Produit").agg(
            Quantite_Totale=("Quantite", "sum"),
            Chiffre_Affaires=("Total", "sum"),
            Nb_Ventes=("Produit", "count")
        ).reset_index().sort_values("Chiffre_Affaires", ascending=False)
        st.dataframe(stats, use_container_width=True)

        st.subheader("👤 Statistiques par vendeur")
        stats_v = df.groupby("Vendeur").agg(
            Chiffre_Affaires=("Total", "sum"),
            Nb_Ventes=("Vendeur", "count")
        ).reset_index().sort_values("Chiffre_Affaires", ascending=False)
        st.dataframe(stats_v, use_container_width=True)

# ═══════════════════════════════════════════
# PAGE 4 : GRAPHIQUES
# ═══════════════════════════════════════════
elif menu == "📈 Graphiques":
    st.header("📈 Visualisation des données")

    if df.empty:
        st.warning("⚠️ Aucune donnée disponible. Enregistrez d'abord des ventes.")
    else:
        df["Total"] = df["Quantite"] * df["Prix_Unitaire"]

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.bar(
                df.groupby("Produit")["Total"].sum().reset_index(),
                x="Produit", y="Total",
                title="💰 Chiffre d'affaires par produit",
                color="Produit"
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.pie(
                df.groupby("Categorie")["Total"].sum().reset_index(),
                names="Categorie", values="Total",
                title="📦 Répartition par catégorie"
            )
            st.plotly_chart(fig2, use_container_width=True)

        fig3 = px.line(
            df.groupby("Date")["Total"].sum().reset_index(),
            x="Date", y="Total",
            title="📅 Évolution des ventes dans le temps",
            markers=True
        )
        st.plotly_chart(fig3, use_container_width=True)
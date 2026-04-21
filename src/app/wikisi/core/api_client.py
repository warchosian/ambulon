"""
WikiSI API client for enumeration and application data management.

This module provides the WikiSIAPIClient class for interacting with WikiSI APIs,
loading enumeration data, and managing application information.
"""

import json
import requests
import os
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def clean_unicode_separators(data: Any) -> Any:
    """
    Nettoie récursivement les caractères Unicode Line Separator (U+2028) et
    Paragraph Separator (U+2029) qui peuvent causer des problèmes dans les éditeurs.

    Ces caractères sont parfois présents dans les données d'API et causent des
    avertissements dans VSCode et d'autres éditeurs.

    Args:
        data: Structure de données (dict, list, str, etc.) à nettoyer

    Returns:
        La même structure avec les caractères LS/PS remplacés par des espaces
    """
    if isinstance(data, str):
        # Remplacer Line Separator (U+2028) et Paragraph Separator (U+2029) par des espaces
        return data.replace('\u2028', ' ').replace('\u2029', ' ')
    elif isinstance(data, dict):
        return {key: clean_unicode_separators(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [clean_unicode_separators(item) for item in data]
    else:
        return data


class WikiSIAPIClient:
    """Client for WikiSI API operations and enumeration management."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_url = config['api']['url']
        self.api_token = config['api']['token']
        self.headers = {
            'User-Agent': config['api']['user_agent'],
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Wikis-API-Key': self.api_token
        }
        self.output_dir = Path(config['output']['directory'])
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Reuse TCP/TLS connection across the dozens of paginated API calls
        self._session = requests.Session()
        self._session.headers.update(self.headers)

        self.enumerations_dict = self._load_or_fetch_enumerations()

    def close(self) -> None:
        """Close the underlying HTTP session."""
        try:
            self._session.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def _load_or_fetch_enumerations(self) -> Dict[str, Any]:
        enum_file = self.output_dir / self.config['output']['enumerations_file']
        if enum_file.exists():
            try:
                with open(enum_file, 'r', encoding='utf-8') as f:
                    logger.info(f"Fichier '{enum_file}' trouvé et chargé.")
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Erreur lors du chargement de '{enum_file}': {e}. Re-construction du fichier...")
                return self._fetch_and_save_enumerations()
        else:
            logger.info(f"Fichier '{enum_file}' non trouvé. Construction du fichier...")
            return self._fetch_and_save_enumerations()

    def _fetch_and_save_enumerations(self) -> Dict[str, Any]:
        data = self.extract_enumerations_dict()
        enum_file = self.output_dir / self.config['output']['enumerations_file']
        # Nettoyer les caractères Unicode problématiques avant la sauvegarde
        cleaned_data = clean_unicode_separators(data)
        with open(enum_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=3)
        logger.info(f"Fichier '{enum_file}' construit et chargé.")
        return data

    def extract_enumerations_dict(self) -> Dict[str, Any]:
        """
        Extrait toutes les instances d'énumération du wiki SI.
        """
        enumerations_dict = {}
        URL = f'{self.api_url}/enumeration/'
        r = self._session.get(URL)
        r.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        result = r.json()
        enumeration_noms = result['enumerations']
        for enumeration_nom in enumeration_noms:
            URL = f'{self.api_url}/enumeration/{enumeration_nom}/'
            r = self._session.get(URL)
            r.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            result = r.json()
            enumeration_objets = result['enumeration']
            enumerations_dict[enumeration_nom] = enumeration_objets
        return enumerations_dict

    def _load_or_fetch_applications(self) -> List[Dict[str, Any]]:
        app_file = self.output_dir / self.config['output']['applications_file']
        if app_file.exists():
            try:
                with open(app_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Fichier '{app_file}' trouvé et chargé.")
                    return data['applications']
            except Exception as e:
                logger.warning(f"Erreur lors du chargement de '{app_file}': {e}. Re-construction du fichier...")
                return self._fetch_and_save_applications()
        else:
            logger.info(f"Fichier '{app_file}' non trouvé. Construction du fichier...")
            return self._fetch_and_save_applications()

    def _fetch_and_save_applications(self) -> List[Dict[str, Any]]:
        app_list = self.extract_applications_list()
        app_file = self.output_dir / self.config['output']['applications_file']
        data = {'applications': app_list}
        # Nettoyer les caractères Unicode problématiques avant la sauvegarde
        cleaned_data = clean_unicode_separators(data)
        with open(app_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=3)
        logger.info(f"Fichier '{app_file}' construit et chargé.")
        return app_list

    def extract_applications_list(self) -> List[Dict[str, Any]]:
        """
        Extrait tous les objets Application du wiki SI.
        """
        applications_list = []
        total_count = None
        offset = 0
        limit = self.config['api'].get('page_limit', 25) # Use config for limit
        while total_count is None or offset < total_count:
            URL = f'{self.api_url}/application/?offset={offset}&limit={limit}'
            r = self._session.get(URL)
            r.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            result = r.json()
            if total_count is None:
                total_count = result['total_count']
            applications = result['applications']
            applications_list.extend(applications)
            offset += limit
        return applications_list

    def get_enumeration_object(self, enumeration_name: str, object_id: str) -> Optional[Dict[str, Any]]:
        if not object_id:
            return None
        objects_enumeration = self.enumerations_dict.get(enumeration_name)
        if not objects_enumeration:
            return None
        for obj in objects_enumeration:
            if obj.get('id') == object_id:
                return obj
        return None

    def get_enumeration_name(self, enumeration_name: str, object_id: str) -> Optional[str]:
        obj = self.get_enumeration_object(enumeration_name, object_id)
        if not obj:
            return None
        return obj.get('nom')

    def generate_application_ia(self, app_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère une forme de l'objet Application adaptée à l'entraînement d'une IA.
        """
        app_ia = {
            'Id': app_json.get('id'),
            'Numéros d\'affaire': [{'Numéro d\'affaire': numAff.get('numAffaire'), 'Commentaire': numAff.get('commentaire')} for numAff in app_json.get('numsAffaire', [])],
            'Ids globaux': [{'Id global': idGlob.get('idGlobal'), 'Commentaire': idGlob.get('commentaire')} for idGlob in app_json.get('idsGlobaux', [])],
            'Nom': app_json.get('nom'),
            'Nom long': app_json.get('nomLong'),
            'Statut SI': self.get_enumeration_name('StatutSI', app_json.get('statutSI_id')),
            'Domaines et sous-domaines': [{'domaine métier': self.get_enumeration_name('DomaineMetier', domSousDom.get('domaineMetier_id')), 'sous-domaine métier': self.get_enumeration_name('SousDomaineMetier', domSousDom.get('sousDomaineMetier_id')), 'Commentaire': domSousDom.get('commentaire')} for domSousDom in app_json.get('domainesSousDomaines', [])],
            'SI métiers et SI fédérateurs': [{'SI métier': self.get_enumeration_name('SIMetier', simSif.get('siMetier_id')), 'SI fédérateur': self.get_enumeration_name('SIFederateur', simSif.get('siFederateur_id')), 'Commentaire': simSif.get('commentaire')} for simSif in app_json.get('siMetiersSiFederateurs', [])],
            'SI à enjeux': 'oui' if app_json.get('siAEnjeux') == True else 'non' if app_json.get('siAEnjeux') == False else None,
            'Application figurant dans les cartographie d\'urbanisme': 'oui' if app_json.get('urba_carto') == True else 'non' if app_json.get('urba_carto') == False else None,
            'POS, zones, quartiers et îlots': [{'POS': self.get_enumeration_name('Urba_POS', posZoneQuartierIlot.get('pos_id')), 'zone': self.get_enumeration_name('Urba_Zone', posZoneQuartierIlot.get('zone_id')), 'quartier': self.get_enumeration_name('Urba_Quartier', posZoneQuartierIlot.get('quartier_id')), 'îlot': self.get_enumeration_name('Urba_Ilot', posZoneQuartierIlot.get('ilot_id')), 'Commentaire': posZoneQuartierIlot.get('commentaire')} for posZoneQuartierIlot in app_json.get('urba_posZonesQuartiersIlots', [])] if app_json.get('urba_posZonesQuartiersIlots') is not None else None,
            'Famille d\'applications': self.get_enumeration_name('FamilleApplication', app_json.get('famille_id')),
            'Descriptif': app_json.get('descriptif'),
            'Hashtags': app_json.get('hashtags'),
            'Objets métiers': [{'Nom de l\'objet métier': objetMetier.get('objetMetier_desc'), 'Objet métier (ID ObjetMetier)': objetMetier.get('objetMetier_id'), 'Commentaire': objetMetier.get('commentaire')} for objetMetier in app_json.get('objetsMetiers', [])],
            'Enjeux': app_json.get('enjeux'),
            'proposition de valeur': app_json.get('propValeur'),
            'Accessibilité': f"{app_json['accessibilite']} %" if app_json.get('accessibilite') is not None else None,
            'Indicateurs': app_json.get('indicateurs'),
            'Obligation': self.get_enumeration_name('Obligation', app_json.get('obligation_id')),
            'Précisions sur l\'obligation': app_json.get('obligation_precisions'),
            'URLs': [{'nature de l\'URL': self.get_enumeration_name('NatureURL', site.get('natureURL_id')), 'URL': site.get('URL'), 'Commentaire': site.get('commentaire')} for site in app_json.get('sites', [])],
            'Courriels': [{'nature du courriel': self.get_enumeration_name('NatureCourriel', courriel.get('natureCourriel_id')), 'courriel': courriel.get('courriel'), 'Commentaire': courriel.get('commentaire')} for courriel in app_json.get('courriels', [])],
            'Portée géographique': self.get_enumeration_name('PorteeGeographique', app_json.get('porteeGeographique_id')),
            'Région de la portée géographique': self.get_enumeration_name('Region', app_json.get('porteeGeographique_region_id')),
            'Précisions sur la portée géographique': app_json.get('porteeGeographique_precisions'),
            'Fonctions': [self.get_enumeration_name('FonctionApplication', fn_id) for fn_id in app_json.get('fonctions', [])],
            'Environnement d\'accès': self.get_enumeration_name('EnvironnementAcces', app_json.get('envAcces_id')),
            'Événements': [{'date': evenement.get('date'), 'type d\'événement': self.get_enumeration_name('TypeEvenement', evenement.get('typeEvenement_id')), 'Version': evenement.get('version'), 'Commentaire': evenement.get('commentaire')} for evenement in app_json.get('evenements', [])],
            'Participe à la cartographie numérique pour la transition écologique': 'oui' if app_json.get('fnv_carto') == True else 'non' if app_json.get('fnv_carto') == False else None,
            'Thématiques et sous-thématiques France Nation Verte': [{'thématique': self.get_enumeration_name('FNV_Thematique', themSousThem.get('thematique_id')), 'sous-thématique': self.get_enumeration_name('FNV_SousThematique', themSousThem.get('sousThematique_id')), 'Commentaire': themSousThem.get('commentaire')} for themSousThem in app_json.get('fnv_thematiquesSousThematiques', [])] if app_json.get('fnv_thematiquesSousThematiques') is not None else None,
            'Catégorisations France Nation Verte': [{'niveau 1': self.get_enumeration_name('FNV_CategorieNiv1', categorisation.get('niveau1_id')), 'niveau 2': self.get_enumeration_name('FNV_CategorieNiv2', categorisation.get('niveau2_id')), 'niveau 3': self.get_enumeration_name('FNV_CategorieNiv3', categorisation.get('niveau3_id')), 'niveau 4': self.get_enumeration_name('FNV_CategorieNiv4', categorisation.get('niveau4_id')), 'Commentaire': categorisation.get('commentaire')} for categorisation in app_json.get('fnv_categorisations', [])] if app_json.get('fnv_categorisations') is not None else None,
            'État des lieux FNV': self.get_enumeration_name('FNV_EtatDesLieux', app_json.get('fnv_etatDesLieux_id')),
            'Précisions sur l\'état des lieux': app_json.get('fnv_etatDesLieux_precisions'),
            'Données liées': [{'type de flux': self.get_enumeration_name('TypeFlux', donneeLiee.get('typeFlux_id')), 'Nom de la donnée liée': donneeLiee.get('donnee_desc'), 'Donnée liée (ID Donnee)': donneeLiee.get('donnee_id'), 'Nom de l\'application 2': donneeLiee.get('application2_desc'), 'Application liée 2 (ID Application)': donneeLiee.get('application2_id'), 'Commentaire': donneeLiee.get('commentaire')} for donneeLiee in app_json.get('donneesLiees', [])],
            'Applications liées': [{'type de lien entre applications': self.get_enumeration_name('TypeLienApplications', appLiee.get('typeLien_id')), 'Nom de l\'application liée 2': appLiee.get('application2_desc'), 'Application liée 2 (ID Application)': appLiee.get('application2_id'), 'Commentaire': appLiee.get('commentaire')} for appLiee in app_json.get('applicationsLiees', [])],
            'Utilisateurs': [{'Utilisateur': self.get_enumeration_name('Utilisateur', utilisateur.get('utilisateur_id')), 'Nombre': utilisateur.get('nombre'), 'Commentaire': utilisateur.get('commentaire')} for utilisateur in app_json.get('utilisateurs', [])],
            'Utilisateurs actifs par mois': app_json.get('utilisateurs_actifsMois'),
            'Précisions sur les utilisateurs': app_json.get('utilisateurs_precisions'),
            'Bénéficiaires': [{'type de lien': self.get_enumeration_name('Beneficiaire', beneficiaire.get('beneficiaire_id')), 'nombre': beneficiaire.get('nombre'), 'Commentaire': beneficiaire.get('commentaire')} for beneficiaire in app_json.get('beneficiaires', [])],
            'Précisions sur les bénéficiaires': app_json.get('beneficiaires_precisions'),
            'Acteurs': [{'rôle d\'acteur': self.get_enumeration_name('TypeRoleActeur', acteur.get('roleActeur_id')), 'acteur': acteur.get('acteur_desc'), 'Commentaire': acteur.get('commentaire')} for acteur in app_json.get('acteurs', [])],
            'Acteurs MOE habilités': [{'acteur': acteur.get('acteur_desc'), 'Commentaire': acteur.get('commentaire')} for acteur in app_json.get('moe_acteursHabilites', [])],
            'Date d\'entrée dans le portefeuille MOE': app_json.get('moe_entreePortefeuille'),
            'Budget MOE en AE': app_json.get('moe_budget_ae'),
            'Nombre d\'ETP MOE internes': app_json.get('moe_etp_internes'),
            'Nombre d\'ETP MOE de prestataires': app_json.get('moe_etp_prestataires'),
            'Équipe MOE': [{'rôle de membre d\'équipe MOE': self.get_enumeration_name('TypeRoleContact', contact.get('roleContact_id')), 'contact': contact.get('contact_desc'), 'courriel': contact.get('courriel'), 'Commentaire': contact.get('commentaire')} for contact in app_json.get('moe_contacts', [])],
            'Rythme et nombre moyen annuel des mises en production': app_json.get('moe_mep_precisions'),
            'Approche produit': 'oui' if app_json.get('moe_approcheProduit') == True else 'non' if app_json.get('moe_approcheProduit') == False else None,
            'Développement agile': 'oui' if app_json.get('moe_agile') == True else 'non' if app_json.get('moe_agile') == False else None,
            'Cahier des charges MOE': 'oui' if app_json.get('moe_cahierDesCharges') == True else 'non' if app_json.get('moe_cahierDesCharges') == False else None,
            'Protocole HTTPS': 'oui' if app_json.get('moe_https') == True else 'non' if app_json.get('moe_https') == False else None,
            'Actions MOE à venir': app_json.get('moe_actions_aVenir'),
            'Actions MOE - Besoins métier, attentes': app_json.get('moe_actions_besoinsMetier'),
            'Actions MOE - refonte': app_json.get('moe_actions_refonte'),
            'Hébergements': [{'type de site': self.get_enumeration_name('TypeSite', hebergement.get('typeSite_id')), 'data center': self.get_enumeration_name('DataCenter', hebergement.get('dataCenter_id')), 'plateforme': self.get_enumeration_name('Plateforme', hebergement.get('plateforme_id')), 'Commentaire': hebergement.get('commentaire')} for hebergement in app_json.get('hebergements', [])],
            'Technologie principale': self.get_enumeration_name('Technologie', app_json.get('technologie_id')),
            'Version de la technologie principale': app_json.get('technologie_version'),
            'Technologies': [{'technologie': self.get_enumeration_name('Technologie', techno.get('technologie_id')), 'version de la technologie': techno.get('technologie_version'), 'Commentaire': techno.get('commentaire')} for techno in app_json.get('technologies', [])],
            'Composants': [{'type de site': self.get_enumeration_name('TypeSite', composant.get('typeSite_id')),'nom du composant': composant.get('composant_desc'), 'ID du composant': composant.get('composant_id'), 'version du composant': composant.get('composant_version'), 'ID du cycle du composant': composant.get('cycle_id'), 'Commentaire': composant.get('commentaire')} for composant in app_json.get('composants', [])] if app_json.get('composants') is not None else None,
            'Codes sources': [{'nom': codeSource.get('nom'), 'licence': self.get_enumeration_name('TypeLicenceCode', codeSource.get('licence_id')), 'URL': codeSource.get('URL'), 'instructions': codeSource.get('instructions')} for codeSource in app_json.get('codesSources', [])],
            'Traitement de données à caractère personnel': 'oui' if app_json.get('rgpd_dacp') == True else 'non' if app_json.get('rgpd_dacp') == False else None,
            'DACP traitées': app_json.get('rgpd_dacp_traitees'),
            'Catégories particulières de DACP': [self.get_enumeration_name('RGPD_CategorieDACP', dacp_categ_id) for dacp_categ_id in app_json.get('rgpd_dacp_categories', [])] if app_json.get('rgpd_dacp_categories') is not None else None,
            'Finalités du traitement': app_json.get('rgpd_traitement_finalites'),
            'Catégories particulières de finalités': [self.get_enumeration_name('RGPD_CategorieFinalite', finalites_categ_id) for finalites_categ_id in app_json.get('rgpd_traitement_finalites_categories', [])],
            'Catégories particulières de traitements': [self.get_enumeration_name('RGPD_CategorieTraitement', traitement_categ_id) for traitement_categ_id in app_json.get('rgpd_traitement_categories', [])],
            'Base juridique du traitement': self.get_enumeration_name('RGPD_BaseJuridiqueTraitement', app_json.get('rgpd_traitement_baseJuridique_id')),
            'Destinataires des données': app_json.get('rgpd_traitement_destinatairesDonnees'),
            'Durée de conservation en années': app_json.get('rgpd_traitement_dureeConservation'),
            'Mode de collecte des informations traitées': self.get_enumeration_name('RGPD_ModeCollecteDonnees', app_json.get('rgpd_traitement_modeCollecteDonnees_id')),
            'Questionnaire préalable - Date de transmission à AJAG1-2': app_json.get('rgpd_questionnairePrealable_transmission'),
            'Date de transmission de la fiche d\'inscription à AJAG1-2': app_json.get('rgpd_registreTraitements_inscription'),
            'Registre des traitements - DatesFiche': app_json.get('rgpd_registreTraitements_datesFiche'),
            'rgpd_registreTraitements_datesInscription': app_json.get('rgpd_registreTraitements_datesInscription'),
            'Registre des traitements - éléments sensibles': app_json.get('rgpd_registreTraitements_elementsSensibles'),
            'Nécessité réglementaire d\'une AIPD': 'oui' if app_json.get('rgpd_aipd') == True else 'non' if app_json.get('rgpd_aipd') == False else None,
            'Justification de l\'AIPD': app_json.get('rgpd_aipd_justification'),
            'Dates des AIPD successives': app_json.get('rgpd_aipd_dates'),
            'Date de transmission de l\'AIPD à la CNIL': app_json.get('rgpd_aipd_transmissionCnil'),
            'Temporalité d\'information des personnes concernées': self.get_enumeration_name('RGPD_ModaliteInfo', app_json.get('rgpd_modaliteInfo_id')),
            'rgpd_modaliteInfo_url': app_json.get('rgpd_modaliteInfo_url'),
            'Envoi de courriels': self.get_enumeration_name('RGPD_ModaliteInfo_EnvoiMails', app_json.get('rgpd_modaliteInfo_envoiMails_id')),
            'URL Mentions légales': app_json.get('rgpd_url_mentionsLegales'),
            'URL Conditions générales d\'utilisation du service': app_json.get('rgpd_url_cgu'),
            'URL Statistiques d\'usages': app_json.get('rgpd_url_stats'),
            'URL Accessibilité + niveau d\'accessibilité': app_json.get('rgpd_url_accessibilite'),
            'Traceurs': app_json.get('rgpd_traceurs_categorie_id'),
            'État de conformité RGPD de l\'usage des traceurs': app_json.get('rgpd_traceurs_conformite_id'),
            'MOA habilitée SSI': [{'acteur': acteur.get('acteur_desc'), 'Commentaire': acteur.get('commentaire')} for acteur in app_json.get('ssi_acteursHabilites', [])],
            'DICT': app_json.get('ssi_dict'),
            ' DICT - disponibilité': app_json.get('ssi_dict_disponibilite_id'),
            'Commentaires sur la disponibilité': app_json.get('ssi_dict_disponibilite_commentaires'),
            'DICT - integrité': app_json.get('ssi_dict_integrite_id'),
            'Commentaires sur l\'integrité': app_json.get('ssi_dict_integrite_commentaires'),
            'DICT- confidentialité': app_json.get('ssi_dict_confidentialite_id'),
            'Commentaires sur la confidentialité': app_json.get('ssi_dict_confidentialite_commentaires'),
            'DICT - traçabilité': app_json.get('ssi_dict_tracabilite_id'),
            'ssi_dict_tracabilite_commentaires': app_json.get('ssi_dict_tracabilite_commentaires'),
            'Études des besoins de sécurité et des risques': [{'date': etude.get('date'), 'type d\'étude': self.get_enumeration_name('SSI_TypeEtudeBesoins', etude.get('typeEtude_id')), 'Commentaire': etude.get('commentaire')} for etude in app_json.get('ssi_etudesBesoinsSecuriteRisques', [])],
            'Audits': [{'date': audit.get('date'), 'type d\'audit': self.get_enumeration_name('SSI_TypeAudit', audit.get('typeAudit_id')), 'Commentaire': audit.get('commentaire')} for audit in app_json.get('ssi_audits', [])],
            'Ce SI bénéficie-t-il de la dispense d\'homologation (Arrêté relatif aux dispenses d\'homologation) ?': 'oui' if app_json.get('ssi_homologation_dispense') == True else 'non' if app_json.get('ssi_homologation_dispense') == False else None,
            'Raison de la dispense d\'homologation': app_json.get('ssi_homologation_dispense_raison'),
            'Situation du SI en regard de l\'homologation de sécurité': app_json.get('ssi_homologation_situation'),
            'Dates des homologations successives': [{'Date de la commission': dates.get('dateCommission'), 'Date du dossier': dates.get('dateDossier'), 'Date de la décision': dates.get('dateDecision'), 'Date d\'expiration': dates.get('dateExpiration'), 'Commentaire': dates.get('commentaire')} for dates in app_json.get('ssi_homologations_dates', [])] if app_json.get('ssi_homologations_dates') is not None else None,
            'Précisions sur les homologations': app_json.get('ssi_homologations_precisions'),
            'Gravités d\'impacts': app_json.get('ssi_gravitesImpacts'),
            'Gravités d\'impacts - Politique Image': app_json.get('ssi_gravitesImpacts_politiqueImage_id'),
            'Commentaires sur les gravités d\'impacts - Politique Image': app_json.get('ssi_gravitesImpacts_politiqueImage_commentaires'),
            'Gravités d\'impacts - Désorganisation interne ou externe': app_json.get('ssi_gravitesImpacts_desorganisation_id'),
            'Commentaires sur les gravités d\'impacts - Désorganisation interne ou externe': app_json.get('ssi_gravitesImpacts_desorganisation_commentaires'),
            'Gravités d\'impacts - Juridique': app_json.get('ssi_gravitesImpacts_juridique_id'),
            'Commentaires sur les gravités d\'impacts - Juridique': app_json.get('ssi_gravitesImpacts_juridique_commentaires'),
            'Gravités d\'impacts - Financier': app_json.get('ssi_gravitesImpacts_financier_id'),
            'Commentaires sur les gravités d\'impacts - Financier': app_json.get('ssi_gravitesImpacts_financier_commentaires'),
            'Gravités d\'impacts - Personnes': app_json.get('ssi_gravitesImpacts_personnes_id'),
            'Commentaires sur les gravités d\'impacts - Personnes': app_json.get('ssi_gravitesImpacts_personnes_commentaires'),
            'Macro-vulnérabilités': app_json.get('ssi_vulnerabilites'),
            'Macro-vulnérabilités - Ouverture': app_json.get('ssi_vulnerabilites_ouverture_id'),
            'ssi_vulnerabilites_ouverture_commentaires': app_json.get('ssi_vulnerabilites_ouverture_commentaires'),
            'Macro-vulnérabilités - Instabilité': app_json.get('ssi_vulnerabilites_instabilite_id'),
            'Commentaires sur les macro-vulnérabilités - Instabilité': app_json.get('ssi_vulnerabilites_instabilite_commentaires'),
            'Macro-vulnérabilités - Authentification': app_json.get('ssi_vulnerabilites_authentification_id'),
            'Commentaires sur les macro-vulnérabilités - Authentification': app_json.get('ssi_vulnerabilites_authentification_commentaires'),
            'Macro-vulnérabilités - Sensibilisation': app_json.get('ssi_vulnerabilites_sensibilisation_id'),
            'Commentaires sur les macro-vulnérabilités - Sensibilisation': app_json.get('ssi_vulnerabilites_sensibilisation_commentaires'),
            'Macro-vulnérabilités - Dette technique': app_json.get('ssi_vulnerabilites_detteTechnique_id'),
            'Commentaires sur les macro-vulnérabilités - Dette technique': app_json.get('ssi_vulnerabilites_detteTechnique_commentaires'),
            'Macro-vulnérabilités - Hébergement': app_json.get('ssi_vulnerabilites_hebergement_id'),
            'Commentaires sur les macro-vulnérabilités - Hébergement': app_json.get('ssi_vulnerabilites_hebergement_commentaires'),
            'Macro-vulnérabilités - Sous-traitance': app_json.get('ssi_vulnerabilites_sousTraitance_id'),
            'Commentaires sur les macro-vulnérabilités - Sous-traitance': app_json.get('ssi_vulnerabilites_sousTraitance_commentaires'),
            'Contacts SSI': [{'rôle de contact': self.get_enumeration_name('TypeRoleContact', contact.get('roleContact_id')), 'contact': contact.get('contact_desc'), 'courriel': contact.get('courriel'), 'Commentaire': contact.get('commentaire')} for contact in app_json.get('ssi_contacts', [])],
            'Cycle de vie des documents et des données': [{'typologie': referentiel.get('typologie'), 'DUA': 'sans limite' if referentiel.get('dua') == 999 else '1 an' if referentiel.get('dua') == 1 else '{} ans'.format(referentiel.get('dua')), 'sort final': self.get_enumeration_name('Arch_SortFinal', referentiel.get('sortFinal_id')), 'justification réglementaire': referentiel.get('justifRegl')} for referentiel in app_json.get('arch_referentiel', [])],
            'Criticité en terme d\'archivage': self.get_enumeration_name('Arch_Criticite', app_json.get('arch_criticite_id')),
            'Archivage - diagnostic': app_json.get('arch_diagnostic'),
            'Archivage - action à mener': self.get_enumeration_name('Arch_Action', app_json.get('arch_action_id')),
            'Évolution technologique': 'oui' if app_json.get('evolutionTechnologique') == True else 'non' if app_json.get('evolutionTechnologique') == False else None,
            'Évolution du contenu': 'oui' if app_json.get('evolutionContenu') == True else 'non' if app_json.get('evolutionContenu') == False else None,
            'Évolution des conditions d\'accès': 'oui' if app_json.get('evolutionConditionsAcces') == True else 'non' if app_json.get('evolutionConditionsAcces') == False else None,
            'Évolution de l\'usage': 'oui' if app_json.get('evolutionUsage') == True else 'non' if app_json.get('evolutionUsage') == False else None,
            'Précisions sur les évolutions': app_json.get('evolutions_precisions'),
            'Contacts': [{'rôle de contact': self.get_enumeration_name('TypeRoleContact', contact.get('roleContact_id')), 'contact': contact.get('contact_desc'), 'courriel': contact.get('courriel'), 'Commentaire': contact.get('commentaire')} for contact in app_json.get('contacts', [])],
            'Date et heure de création de la fiche': app_json.get('creationFiche'),
            'Date et heure de modification de la fiche': app_json.get('modificationFiche')
        }
        return app_ia

    def generate_applications_ia_list(self, applications_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Génère une forme "textuelle" de l\'objet Application adaptée à l\'entraînement d\'une IA.
        """
        applicationsIA_list = []
        for application in applications_list:
            app_ia = self.generate_application_ia(application)
            applicationsIA_list.append(app_ia)
        return applicationsIA_list

    def save_applications_ia_list(self, applications_list: List[Dict[str, Any]]):
        """
        Sauve dans un fichier les objets "textuels" des objets Application du wiki SI.
        """
        fileName = self.output_dir / self.config['output']['applications_ia_file']
        app_ia_list = self.generate_applications_ia_list(applications_list)
        data = {
            'applicationsIA': app_ia_list
        }
        # Nettoyer les caractères Unicode problématiques avant la sauvegarde
        cleaned_data = clean_unicode_separators(data)
        with open(fileName, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=3)
        logger.info(f"Fichier '{fileName}' construit et chargé.")

    def generate_application_ia_mini(self, app_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère une forme de l\'objet Application sans les champs vides adaptée à l\'entraînement d\'une IA.
        """
        app_ia = {}
        if app_json.get('id'):
            app_ia['Id'] = app_json['id']
        if app_json.get('numsAffaire'):
            obj_list = []
            for numAff in app_json['numsAffaire']:
                obj_dict = {}
                if numAff.get('numAffaire'):
                    obj_dict['Numéro d\'affaire'] = numAff['numAffaire']
                if numAff.get('commentaire'):
                    obj_dict['Commentaire'] = numAff['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Numéros d\'affaire'] = obj_list
        if app_json.get('idsGlobaux'):
            obj_list = []
            for idGlob in app_json['idsGlobaux']:
                obj_dict = {}
                if idGlob.get('idGlobal'):
                    obj_dict['Id global'] = idGlob['idGlobal']
                if idGlob.get('commentaire'):
                    obj_dict['Commentaire'] = idGlob['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Ids globaux'] = obj_list
        if app_json.get('nom'):
            app_ia['Nom'] = app_json['nom']
        if app_json.get('nomLong'):
            app_ia['Nom long'] = app_json['nomLong']
        if app_json.get('statutSI_id'):
            app_ia['Statut SI'] = self.get_enumeration_name('StatutSI', app_json['statutSI_id'])
        if app_json.get('domainesSousDomaines'):
            obj_list = []
            for domSousDom in app_json['domainesSousDomaines']:
                obj_dict = {}
                if domSousDom.get('domaineMetier_id'):
                    obj_dict['Domaine métier'] = self.get_enumeration_name('DomaineMetier', domSousDom['domaineMetier_id'])
                if domSousDom.get('sousDomaineMetier_id'):
                    obj_dict['sous-domaine métier'] = self.get_enumeration_name('SousDomaineMetier', domSousDom['sousDomaineMetier_id'])
                if domSousDom.get('commentaire'):
                    obj_dict['Commentaire'] = domSousDom['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Domaines et sous-domaines'] = obj_list
        if app_json.get('siMetiersSiFederateurs'):
            obj_list = []
            for simSif in app_json['siMetiersSiFederateurs']:
                obj_dict = {}
                if simSif.get('siMetier_id'):
                    obj_dict['SI métier'] = self.get_enumeration_name('SIMetier', simSif['siMetier_id'])
                if simSif.get('siFederateur_id'):
                    obj_dict['SI fédérateur'] = self.get_enumeration_name('SIFederateur', simSif['siFederateur_id'])
                if simSif.get('commentaire'):
                    obj_dict['Commentaire'] = simSif['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['SI métiers et SI fédérateurs'] = obj_list
        if app_json.get('siAEnjeux') is not None:
            app_ia['SI à enjeux'] = 'oui' if app_json.get('siAEnjeux') == True else 'non' if app_json.get('siAEnjeux') == False else None
        if app_json.get('urba_carto') is not None:
            app_ia['Application figurant dans les cartographie d\'urbanisme'] = 'oui' if app_json.get('urba_carto') == True else 'non' if app_json.get('urba_carto') == False else None
        if app_json.get('urba_posZonesQuartiersIlots'):
            obj_list = []
            for posZoneQuartierIlot in app_json['urba_posZonesQuartiersIlots']:
                obj_dict = {}
                if posZoneQuartierIlot.get('pos_id'):
                    obj_dict['POS'] = self.get_enumeration_name('Urba_POS', posZoneQuartierIlot['pos_id'])
                if posZoneQuartierIlot.get('zone_id'):
                    obj_dict['Zone'] = self.get_enumeration_name('Urba_Zone', posZoneQuartierIlot['zone_id'])
                if posZoneQuartierIlot.get('quartier_id'):
                    obj_dict['Quartier'] = self.get_enumeration_name('Urba_Quartier', posZoneQuartierIlot['quartier_id'])
                if posZoneQuartierIlot.get('ilot_id'):
                    obj_dict['Îlot'] = self.get_enumeration_name('Urba_Ilot', posZoneQuartierIlot['ilot_id'])
                if posZoneQuartierIlot.get('commentaire'):
                    obj_dict['Commentaire'] = posZoneQuartierIlot['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['POS, zones, quartiers et îlots'] = obj_list
        if app_json.get('famille_id'):
            app_ia['Famille d\'applications'] = self.get_enumeration_name('FamilleApplication', app_json['famille_id'])
        if app_json.get('descriptif'):
            app_ia['Descriptif'] = app_json['descriptif']
        if app_json.get('hashtags'):
            app_ia['Hashtags'] = app_json['hashtags']
        if app_json.get('objetsMetiers'):
            obj_list = []
            for objetMetier in app_json['objetsMetiers']:
                obj_dict = {}
                if objetMetier.get('objetMetier_desc'):
                    obj_dict['Nom de l\'objet métier'] = objetMetier['objetMetier_desc']
                if objetMetier.get('objetMetier_id'):
                    obj_dict['ID objet métier'] = objetMetier['objetMetier_id']
                if objetMetier.get('commentaire'):
                    obj_dict['Commentaire'] = objetMetier['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Données liées'] = obj_list
        if app_json.get('enjeux'):
            app_ia['Enjeux'] = app_json['enjeux']
        if app_json.get('propValeur'):
            app_ia['proposition de valeur'] = app_json['propValeur']
        if app_json.get('accessibilite') is not None:
            app_ia['Accessibilité'] = f"{app_json['accessibilite']} %" if app_json['accessibilite'] is not None else None
        if app_json.get('indicateurs'):
            obj_list = []
            for indic in app_json['indicateurs']:
                obj_dict = {}
                if indic.get('indicateur'):
                    obj_dict['Indicateur'] = indic['indicateur']
                if indic.get('valeur'):
                    obj_dict['Valeur'] = indic['valeur']
                if indic.get('commentaire'):
                    obj_dict['Commentaire'] = indic['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Indicateurs'] = obj_list
        if app_json.get('obligation_id'):
            app_ia['Obligation'] = self.get_enumeration_name('Obligation', app_json['obligation_id'])
        if app_json.get('obligation_precisions'):
            app_ia['Précisions sur l\'obligation'] = app_json['obligation_precisions']
        if app_json.get('sites'):
            obj_list = []
            for site in app_json['sites']:
                obj_dict = {}
                if site.get('natureURL_id'):
                    obj_dict['nature de l\'URL'] = self.get_enumeration_name('NatureURL', site['natureURL_id'])
                if site.get('URL'):
                    obj_dict['URL'] = site['URL']
                if site.get('commentaire'):
                    obj_dict['Commentaire'] = site['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Sites'] = obj_list
        if app_json.get('courriels'):
            obj_list = []
            for courriel in app_json['courriels']:
                obj_dict = {}
                if courriel.get('natureCourriel_id'):
                    obj_dict['Nature du courriel'] = self.get_enumeration_name('NatureCourriel', courriel['natureCourriel_id'])
                if courriel.get('courriel'):
                    obj_dict['Courriel'] = courriel['courriel']
                if courriel.get('commentaire'):
                    obj_dict['Commentaire'] = courriel['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Courriels'] = obj_list
        if app_json.get('porteeGeographique_id'):
            app_ia['Portée géographique'] = self.get_enumeration_name('PorteeGeographique', app_json['porteeGeographique_id'])
        if app_json.get('porteeGeographique_region_id'):
            app_ia['Région de la portée géographique'] = self.get_enumeration_name('Region', app_json['porteeGeographique_region_id'])
        if app_json.get('porteeGeographique_precisions'):
            app_ia['Précisions sur la portée géographique'] = app_json['porteeGeographique_precisions']
        if app_json.get('fonctions'):
            app_ia['Fonctions'] = [self.get_enumeration_name('FonctionApplication', fn_id) for fn_id in app_json['fonctions']]
        if app_json.get('envAcces_id'):
            app_ia['Environnement d\'accès'] = self.get_enumeration_name('EnvironnementAcces', app_json['envAcces_id'])
        if app_json.get('evenements'):
            obj_list = []
            for evenement in app_json['evenements']:
                obj_dict = {}
                if evenement.get('date'):
                    obj_dict['Date'] = evenement['date']
                if evenement.get('typeEvenement_id'):
                    obj_dict['Type d\'événement'] = self.get_enumeration_name('TypeEvenement', evenement['typeEvenement_id'])
                if evenement.get('version'):
                    obj_dict['Version'] = evenement['version']
                if evenement.get('commentaire'):
                    obj_dict['Commentaire'] = evenement['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Événements'] = obj_list
        if app_json.get('fnv_carto') is not None:
            app_ia['Participe à la cartographie numérique pour la transition écologique'] = 'oui' if app_json.get('fnv_carto') == True else 'non' if app_json.get('fnv_carto') == False else None
        if app_json.get('fnv_thematiquesSousThematiques'):
            obj_list = []
            for themSousThem in app_json['fnv_thematiquesSousThematiques']:
                obj_dict = {}
                if themSousThem.get('thematique_id'):
                    obj_dict['Thématique'] = self.get_enumeration_name('FNV_Thematique', themSousThem['thematique_id'])
                if themSousThem.get('sousThematique_id'):
                    obj_dict['Sous-thématique'] = self.get_enumeration_name('FNV_SousThematique', themSousThem['sousThematique_id'])
                if themSousThem.get('commentaire'):
                    obj_dict['Commentaire'] = themSousThem['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Thématiques et sous-thématiques France Nation Verte'] = obj_list
        if app_json.get('fnv_categorisations'):
            obj_list = []
            for categorisation in app_json['fnv_categorisations']:
                obj_dict = {}
                if categorisation.get('niveau1_id'):
                    obj_dict['Niveau 1'] = self.get_enumeration_name('FNV_CategorieNiv1', categorisation['niveau1_id'])
                if categorisation.get('niveau2_id'):
                    obj_dict['Niveau 2'] = self.get_enumeration_name('FNV_CategorieNiv2', categorisation['niveau2_id'])
                if categorisation.get('niveau3_id'):
                    obj_dict['Niveau 3'] = self.get_enumeration_name('FNV_CategorieNiv3', categorisation['niveau3_id'])
                if categorisation.get('niveau4_id'):
                    obj_dict['Niveau 4'] = self.get_enumeration_name('FNV_CategorieNiv4', categorisation['niveau4_id'])
                if categorisation.get('commentaire'):
                    obj_dict['Commentaire'] = categorisation['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Catégorisations France Nation Verte'] = obj_list
        if app_json.get('fnv_etatDesLieux_id'):
            app_ia['État des lieux FNV'] = self.get_enumeration_name('FNV_EtatDesLieux', app_json['fnv_etatDesLieux_id'])
        if app_json.get('fnv_etatDesLieux_precisions'):
            app_ia['Précisions sur l\'état des lieux'] = app_json['fnv_etatDesLieux_precisions']
        if app_json.get('donneesLiees'):
            obj_list = []
            for donneeLiee in app_json['donneesLiees']:
                obj_dict = {}
                if donneeLiee.get('typeFlux_id'):
                    obj_dict['Type de flux'] = self.get_enumeration_name('TypeFlux', donneeLiee['typeFlux_id'])
                if donneeLiee.get('donnee_desc'):
                    obj_dict['Donnée liée'] = donneeLiee['donnee_desc']
                if donneeLiee.get('donnee_id'):
                    obj_dict['ID donnée liée'] = donneeLiee['donnee_id']
                if donneeLiee.get('application2_desc'):
                    obj_dict['Application 2'] = donneeLiee['application2_desc']
                if donneeLiee.get('application2_id'):
                    obj_dict['ID application 2'] = donneeLiee['application2_id']
                if donneeLiee.get('commentaire'):
                    obj_dict['Commentaire'] = donneeLiee['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Données liées'] = obj_list
        if app_json.get('applicationsLiees'):
            obj_list = []
            for appLiee in app_json['applicationsLiees']:
                obj_dict = {}
                if appLiee.get('typeLien_id'):
                    obj_dict['Type de flux'] = self.get_enumeration_name('TypeLienApplications', appLiee['typeLien_id'])
                if appLiee.get('application2_desc'):
                    obj_dict['Application 2'] = appLiee['application2_desc']
                if appLiee.get('application2_id'):
                    obj_dict['ID application 2'] = appLiee['application2_id']
                if appLiee.get('commentaire'):
                    obj_dict['Commentaire'] = appLiee['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Applications liées'] = obj_list
        if app_json.get('utilisateurs'):
            obj_list = []
            for utilisateur in app_json['utilisateurs']:
                obj_dict = {}
                if utilisateur.get('utilisateur_id'):
                    obj_dict['Utilisateur'] = self.get_enumeration_name('Utilisateur', utilisateur['utilisateur_id'])
                if utilisateur.get('nombre'):
                    obj_dict['Nombre'] = utilisateur['nombre']
                if utilisateur.get('commentaire'):
                    obj_dict['Commentaire'] = utilisateur['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Utilisateurs'] = obj_list
        if app_json.get('utilisateurs_actifsMois'):
            app_ia['Utilisateurs actifs par mois'] = app_json['utilisateurs_actifsMois']
        if app_json.get('utilisateurs_precisions'):
            app_ia['Précisions sur les utilisateurs'] = app_json['utilisateurs_precisions']
        if app_json.get('beneficiaires'):
            obj_list = []
            for beneficiaire in app_json['beneficiaires']:
                obj_dict = {}
                if beneficiaire.get('beneficiaire_id'):
                    obj_dict['Bénéficiaire'] = self.get_enumeration_name('Beneficiaire', beneficiaire['beneficiaire_id'])
                if beneficiaire.get('nombre'):
                    obj_dict['Nombre'] = beneficiaire['nombre']
                if beneficiaire.get('commentaire'):
                    obj_dict['Commentaire'] = beneficiaire['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Bénéficiaires'] = obj_list
        if app_json.get('beneficiaires_precisions'):
            app_ia['Précisions sur les bénéficiaires'] = app_json['beneficiaires_precisions']
        if app_json.get('acteurs'):
            obj_list = []
            for acteur in app_json['acteurs']:
                obj_dict = {}
                if acteur.get('roleActeur_id'):
                    obj_dict['Rôle d\'acteur'] = self.get_enumeration_name('TypeRoleActeur', acteur['roleActeur_id'])
                if acteur.get('acteur_desc'):
                    obj_dict['Acteur'] = acteur['acteur_desc']
                if acteur.get('commentaire'):
                    obj_dict['Commentaire'] = acteur['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Acteurs'] = obj_list
        if app_json.get('moe_acteursHabilites'):
            obj_list = []
            for acteur in app_json['moe_acteursHabilites']:
                obj_dict = {}
                if acteur.get('acteur_desc'):
                    obj_dict['Acteur'] = acteur['acteur_desc']
                if acteur.get('commentaire'):
                    obj_dict['Commentaire'] = acteur['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Acteurs MOE habilités'] = obj_list
        if app_json.get('moe_entreePortefeuille'):
            app_ia['Date d\'entrée dans le portefeuille MOE'] = app_json['moe_entreePortefeuille']
        if app_json.get('moe_budget_ae'):
            app_ia['Budget MOE en AE'] = app_json['moe_budget_ae']
        if app_json.get('moe_etp_internes'):
            app_ia['Nombre d\'ETP MOE internes'] = app_json['moe_etp_internes']
        if app_json.get('moe_etp_prestataires'):
            app_ia['Nombre d\'ETP MOE de prestataires'] = app_json['moe_etp_prestataires']
        if app_json.get('moe_contacts'):
            obj_list = []
            for contact in app_json['moe_contacts']:
                obj_dict = {}
                if contact.get('roleContact_id'):
                    obj_dict['Rôle de membre d\'équipe MOE'] = self.get_enumeration_name('TypeRoleContact', contact['roleContact_id'])
                if contact.get('contact_desc'):
                    obj_dict['Contact'] = contact['contact_desc']
                if contact.get('courriel'):
                    obj_dict['Courriel'] = contact['courriel']
                if contact.get('commentaire'):
                    obj_dict['Commentaire'] = contact['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Équipe MOE'] = obj_list
        if app_json.get('moe_mep_precisions'):
            app_ia['Rythme et nombre moyen annuel des mises en production'] = app_json['moe_mep_precisions']
        if app_json.get('moe_approcheProduit') is not None:
            app_ia['Approche produit'] = 'oui' if app_json.get('moe_approcheProduit') == True else 'non' if app_json.get('moe_approcheProduit') == False else None
        if app_json.get('moe_agile') is not None:
            app_ia['Développement agile'] = 'oui' if app_json.get('moe_agile') == True else 'non' if app_json.get('moe_agile') == False else None
        if app_json.get('moe_cahierDesCharges') is not None:
            app_ia['Cahier des charges MOE'] = 'oui' if app_json.get('moe_cahierDesCharges') == True else 'non' if app_json.get('moe_cahierDesCharges') == False else None
        if app_json.get('moe_https') is not None:
            app_ia['Protocole HTTPS'] = 'oui' if app_json.get('moe_https') == True else 'non' if app_json.get('moe_https') == False else None
        if app_json.get('moe_actions_aVenir'):
            app_ia['Actions MOE à venir'] = app_json['moe_actions_aVenir']
        if app_json.get('moe_actions_besoinsMetier'):
            app_ia['Actions MOE - Besoins métier, attentes'] = app_json['moe_actions_besoinsMetier']
        if app_json.get('moe_actions_refonte'):
            app_ia['Actions MOE - refonte'] = app_json['moe_actions_refonte']
        if app_json.get('hebergements'):
            obj_list = []
            for hebergement in app_json['hebergements']:
                obj_dict = {}
                if hebergement.get('typeSite_id'):
                    obj_dict['Type de site'] = self.get_enumeration_name('TypeSite', hebergement['typeSite_id'])
                if hebergement.get('dataCenter_id'):
                    obj_dict['Data center'] = self.get_enumeration_name('DataCenter', hebergement['dataCenter_id'])
                if hebergement.get('plateforme_id'):
                    obj_dict['Plateforme'] = self.get_enumeration_name('Plateforme', hebergement['plateforme_id'])
                if hebergement.get('commentaire'):
                    obj_dict['Commentaire'] = hebergement['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Hébergements'] = obj_list
        if app_json.get('technologie_id'):
            app_ia['Technologie principale'] = self.get_enumeration_name('Technologie', app_json['technologie_id'])
        if app_json.get('technologie_version'):
            app_ia['Version de la technologie principale'] = app_json['technologie_version']
        if app_json.get('technologies'):
            obj_list = []
            for techno in app_json['technologies']:
                obj_dict = {}
                if techno.get('technologie_id'):
                    obj_dict['Technologie'] = self.get_enumeration_name('Technologie', techno['technologie_id'])
                if techno.get('technologie_version'):
                    obj_dict['Version de la technologie'] = techno['technologie_version']
                if techno.get('commentaire'):
                    obj_dict['Commentaire'] = techno['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Technologies'] = obj_list
        if app_json.get('composants'):
            obj_list = []
            for composant in app_json['composants']:
                obj_dict = {}
                if composant.get('composant_desc'):
                    obj_dict['Nom du composant'] = composant['composant_desc']
                if composant.get('composant_id'):
                    obj_dict['ID composant'] = composant['composant_id']
                if composant.get('composant_version'):
                    obj_dict['Version du composant'] = composant['composant_version']
                if composant.get('cycle_id'):
                    obj_dict['ID cycle'] = composant['cycle_id']
                if composant.get('commentaire'):
                    obj_dict['Commentaire'] = composant['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Composants'] = obj_list
        if app_json.get('codesSources'):
            obj_list = []
            for codeSource in app_json['codesSources']:
                obj_dict = {}
                if codeSource.get('nom'):
                    obj_dict['Nom'] = codeSource['nom']
                if codeSource.get('licence_id'):
                    obj_dict['Licence'] = self.get_enumeration_name('TypeLicenceCode', codeSource['licence_id'])
                if codeSource.get('URL'):
                    obj_dict['URL'] = codeSource['URL']
                if codeSource.get('instructions'):
                    obj_dict['Instructions'] = codeSource['instructions']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Codes sources'] = obj_list
        if app_json.get('rgpd_dacp') is not None:
            app_ia['Traitement de données à caractère personnel'] = 'oui' if app_json.get('rgpd_dacp') == True else 'non' if app_json.get('rgpd_dacp') == False else None
        if app_json.get('rgpd_dacp_traitees'):
            app_ia['DACP traitées'] = app_json['rgpd_dacp_traitees']
        if app_json.get('rgpd_dacp_categories'):
            app_ia['Catégories particulières de DACP'] = [self.get_enumeration_name('RGPD_CategorieDACP', dacp_categ_id) for dacp_categ_id in app_json['rgpd_dacp_categories']]
        if app_json.get('rgpd_traitement_finalites'):
            app_ia['Finalités du traitement'] = app_json['rgpd_traitement_finalites']
        if app_json.get('rgpd_traitement_finalites_categories'):
            app_ia['Catégories particulières de finalités'] = [self.get_enumeration_name('RGPD_CategorieFinalite', finalites_categ_id) for finalites_categ_id in app_json['rgpd_traitement_finalites_categories']]
        if app_json.get('rgpd_traitement_categories'):
            app_ia['Catégories particulières de traitements'] = [self.get_enumeration_name('RGPD_CategorieTraitement', traitement_categ_id) for traitement_categ_id in app_json['rgpd_traitement_categories']]
        if app_json.get('rgpd_traitement_baseJuridique_id'):
            app_ia['Base juridique du traitement'] = self.get_enumeration_name('RGPD_BaseJuridiqueTraitement', app_json['rgpd_traitement_baseJuridique_id'])
        if app_json.get('rgpd_traitement_destinatairesDonnees'):
            app_ia['Destinataires des données'] = app_json['rgpd_traitement_destinatairesDonnees']
        if app_json.get('rgpd_traitement_dureeConservation'):
            app_ia['Durée de conservation en années'] = app_json['rgpd_traitement_dureeConservation']
        if app_json.get('rgpd_traitement_modeCollecteDonnees_id'):
            app_ia['Mode de collecte des informations traitées'] = self.get_enumeration_name('RGPD_ModeCollecteDonnees', app_json['rgpd_traitement_modeCollecteDonnees_id'])
        if app_json.get('rgpd_questionnairePrealable_transmission'):
            app_ia['Questionnaire préalable - Date de transmission à AJAG1-2'] = app_json['rgpd_questionnairePrealable_transmission']
        if app_json.get('rgpd_registreTraitements_inscription'):
            app_ia['Date de transmission de la fiche d\'inscription à AJAG1-2'] = app_json['rgpd_registreTraitements_inscription']
        if app_json.get('rgpd_registreTraitements_datesFiche'):
            obj_list = []
            for dateFiche in app_json['rgpd_registreTraitements_datesFiche']:
                obj_dict = {}
                if dateFiche.get('date'):
                    obj_dict['Date'] = dateFiche['date']
                if dateFiche.get('commentaire'):
                    obj_dict['Commentaire'] = dateFiche['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Dates de création/mise à jour de la fiche d\'inscription'] = obj_list
        if app_json.get('rgpd_registreTraitements_datesInscription'):
            obj_list = []
            for dateRegistre in app_json['rgpd_registreTraitements_datesInscription']: # Changed from rgpd_registreTraitements_datesFiche to rgpd_registreTraitements_datesInscription
                obj_dict = {}
                if dateRegistre.get('date'):
                    obj_dict['Date'] = dateRegistre['date']
                if dateRegistre.get('commentaire'):
                    obj_dict['Commentaire'] = dateRegistre['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Dates d\'inscription/modification du registre des traitements - ']= obj_list
        if app_json.get('rgpd_registreTraitements_elementsSensibles'):
            app_ia['Registre des traitements - éléments sensibles'] = app_json['rgpd_registreTraitements_elementsSensibles']
        if app_json.get('rgpd_aipd') is not None:
            app_ia['Nécessité réglementaire d\'une AIPD'] = 'oui' if app_json.get('rgpd_aipd') == True else 'non' if app_json.get('rgpd_aipd') == False else None
        if app_json.get('rgpd_aipd_justification'):
            app_ia['Justification de l\'AIPD'] = app_json['rgpd_aipd_justification']
        if app_json.get('rgpd_aipd_dates'):
            obj_list = []
            for aipd_date in app_json['rgpd_aipd_dates']:
                obj_dict = {}
                if aipd_date.get('date'):
                    obj_dict['Date'] = aipd_date['date']
                if aipd_date.get('commentaire'):
                    obj_dict['Commentaire'] = aipd_date['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Dates des AIPD successives'] = obj_list
        if app_json.get('rgpd_aipd_transmissionCnil'):
            app_ia['Date de transmission de l\'AIPD à la CNIL'] = app_json['rgpd_aipd_transmissionCnil']
        if app_json.get('rgpd_modaliteInfo_id'):
            app_ia['Temporalité d\'information des personnes concernées'] = self.get_enumeration_name('RGPD_ModaliteInfo', app_json['rgpd_modaliteInfo_id'])
        if app_json.get('rgpd_modaliteInfo_url'):
            app_ia['rgpd_modaliteInfo_url'] = app_json['rgpd_modaliteInfo_url']
        if app_json.get('rgpd_modaliteInfo_envoiMails_id'):
            app_ia['Envoi de courriels'] = self.get_enumeration_name('RGPD_ModaliteInfo_EnvoiMails', app_json['rgpd_modaliteInfo_envoiMails_id'])
        if app_json.get('rgpd_url_mentionsLegales'):
            app_ia['URL Mentions légales'] = app_json['rgpd_url_mentionsLegales']
        if app_json.get('rgpd_url_cgu'):
            app_ia['URL Conditions générales d\'utilisation du service'] = app_json['rgpd_url_cgu']
        if app_json.get('rgpd_url_stats'):
            app_ia['URL Statistiques d\'usages'] = app_json['rgpd_url_stats']
        if app_json.get('rgpd_url_accessibilite'):
            app_ia['URL Accessibilité + niveau d\'accessibilité'] = app_json['rgpd_url_accessibilite']
        if app_json.get('rgpd_traceurs_categorie_id'):
            app_ia['Traceurs'] = app_json['rgpd_traceurs_categorie_id']
        if app_json.get('rgpd_traceurs_conformite_id'):
            app_ia['État de conformité RGPD de l\'usage des traceurs'] = app_json['rgpd_traceurs_conformite_id']
        if app_json.get('ssi_acteursHabilites'):
            obj_list = []
            for acteur in app_json['ssi_acteursHabilites']:
                obj_dict = {}
                if acteur.get('acteur_desc'):
                    obj_dict['Acteur'] = acteur['acteur_desc']
                if acteur.get('commentaire'):
                    obj_dict['Commentaire'] = acteur['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['MOA habilitée SSI'] = obj_list
        if app_json.get('ssi_dict'):
            app_ia['DICT'] = app_json['ssi_dict']
        if app_json.get('ssi_dict_disponibilite_id'):
            app_ia[' DICT - disponibilité'] = app_json['ssi_dict_disponibilite_id']
        if app_json.get('ssi_dict_disponibilite_commentaires'):
            app_ia['Commentaires sur la disponibilité'] = app_json['ssi_dict_disponibilite_commentaires']
        if app_json.get('ssi_dict_integrite_id'):
            app_ia['DICT - integrité'] = app_json['ssi_dict_integrite_id']
        if app_json.get('ssi_dict_integrite_commentaires'):
            app_ia['Commentaires sur l\'integrité'] = app_json['ssi_dict_integrite_commentaires']
        if app_json.get('ssi_dict_confidentialite_id'):
            app_ia['DICT- confidentialité'] = app_json['ssi_dict_confidentialite_id']
        if app_json.get('ssi_dict_confidentialite_commentaires'):
            app_ia['Commentaires sur la confidentialité'] = app_json['ssi_dict_confidentialite_commentaires']
        if app_json.get('ssi_dict_tracabilite_id'):
            app_ia['DICT - traçabilité'] = app_json['ssi_dict_tracabilite_id']
        if app_json.get('ssi_dict_tracabilite_commentaires'):
            app_ia['ssi_dict_tracabilite_commentaires'] = app_json['ssi_dict_tracabilite_commentaires']
        if app_json.get('ssi_etudesBesoinsSecuriteRisques'):
            obj_list = []
            for etude in app_json['ssi_etudesBesoinsSecuriteRisques']:
                obj_dict = {}
                if etude.get('date'):
                    obj_dict['Date'] = etude['date']
                if etude.get('typeEtude_id'):
                    obj_dict['Type d\'étude'] = self.get_enumeration_name('SSI_TypeEtudeBesoins', etude['typeEtude_id'])
                if etude.get('commentaire'):
                    obj_dict['Commentaire'] = etude['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Études des besoins de sécurité et des risques'] = obj_list
        if app_json.get('ssi_audits'):
            obj_list = []
            for audit in app_json['ssi_audits']:
                obj_dict = {}
                if audit.get('date'):
                    obj_dict['Date'] = audit['date']
                if audit.get('typeAudit_id'):
                    obj_dict['Type d\'audit'] = self.get_enumeration_name('SSI_TypeAudit', audit['typeAudit_id'])
                if audit.get('commentaire'):
                    obj_dict['Commentaire'] = audit['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Audits'] = obj_list
        if app_json.get('ssi_homologation_dispense') is not None:
            app_ia['Ce SI bénéficie-t-il de la dispense d\'homologation (Arrêté relatif aux dispenses d\'homologation) ?'] = 'oui' if app_json.get('ssi_homologation_dispense') == True else 'non' if app_json.get('ssi_homologation_dispense') == False else None
        if app_json.get('ssi_homologation_dispense_raison'):
            app_ia['Raison de la dispense d\'homologation'] = app_json['ssi_homologation_dispense_raison']
        if app_json.get('ssi_homologation_situation'):
            app_ia['Situation du SI en regard de l\'homologation de sécurité'] = app_json['ssi_homologation_situation']
        if app_json.get('ssi_homologations_dates'):
            obj_list = []
            for dates in app_json['ssi_homologations_dates']:
                obj_dict = {}
                if dates.get('dateCommission'):
                    obj_dict['Date de la commission'] = dates['dateCommission']
                if dates.get('dateDossier'):
                    obj_dict['Date du dossier'] = dates['dateDossier']
                if dates.get('dateDecision'):
                    obj_dict['Date de la décision'] = dates['dateDecision']
                if dates.get('dateExpiration'):
                    obj_dict['Date d\'expiration'] = dates['dateExpiration']
                if dates.get('commentaire'):
                    obj_dict['Commentaire'] = dates['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Dates des homologations successives'] = obj_list
        if app_json.get('ssi_homologations_precisions'):
            app_ia['Précisions sur les homologations'] = app_json['ssi_homologations_precisions']
        if app_json.get('ssi_gravitesImpacts'):
            app_ia['Gravités d\'impacts'] = app_json['ssi_gravitesImpacts']
        if app_json.get('ssi_gravitesImpacts_politiqueImage_id'):
            app_ia['Gravités d\'impacts - Politique Image'] = app_json['ssi_gravitesImpacts_politiqueImage_id']
        if app_json.get('ssi_gravitesImpacts_politiqueImage_commentaires'):
            app_ia['Commentaires sur les gravités d\'impacts - Politique Image'] = app_json['ssi_gravitesImpacts_politiqueImage_commentaires']
        if app_json.get('ssi_gravitesImpacts_desorganisation_id'):
            app_ia['Gravités d\'impacts - Désorganisation interne ou externe'] = app_json['ssi_gravitesImpacts_desorganisation_id']
        if app_json.get('ssi_gravitesImpacts_desorganisation_commentaires'):
            app_ia['Commentaires sur les gravités d\'impacts - Désorganisation interne ou externe'] = app_json['ssi_gravitesImpacts_desorganisation_commentaires']
        if app_json.get('ssi_gravitesImpacts_juridique_id'):
            app_ia['Gravités d\'impacts - Juridique'] = app_json['ssi_gravitesImpacts_juridique_id']
        if app_json.get('ssi_gravitesImpacts_juridique_commentaires'):
            app_ia['Commentaires sur les gravités d\'impacts - Juridique'] = app_json['ssi_gravitesImpacts_juridique_commentaires']
        if app_json.get('ssi_gravitesImpacts_financier_id'):
            app_ia['Gravités d\'impacts - Financier'] = app_json['ssi_gravitesImpacts_financier_id']
        if app_json.get('ssi_gravitesImpacts_financier_commentaires'):
            app_ia['Commentaires sur les gravités d\'impacts - Financier'] = app_json['ssi_gravitesImpacts_financier_commentaires']
        if app_json.get('ssi_gravitesImpacts_personnes_id'):
            app_ia['Gravités d\'impacts - Personnes'] = app_json['ssi_gravitesImpacts_personnes_id']
        if app_json.get('ssi_gravitesImpacts_personnes_commentaires'):
            app_ia['Commentaires sur les gravités d\'impacts - Personnes'] = app_json['ssi_gravitesImpacts_personnes_commentaires']
        if app_json.get('ssi_vulnerabilites'):
            app_ia['Macro-vulnérabilités'] = app_json['ssi_vulnerabilites']
        if app_json.get('ssi_vulnerabilites_ouverture_id'):
            app_ia['Macro-vulnérabilités - Ouverture'] = app_json['ssi_vulnerabilites_ouverture_id']
        if app_json.get('ssi_vulnerabilites_ouverture_commentaires'):
            app_ia['ssi_vulnerabilites_ouverture_commentaires'] = app_json['ssi_vulnerabilites_ouverture_commentaires']
        if app_json.get('ssi_vulnerabilites_instabilite_id'):
            app_ia['Macro-vulnérabilités - Instabilité'] = app_json['ssi_vulnerabilites_instabilite_id']
        if app_json.get('ssi_vulnerabilites_instabilite_commentaires'):
            app_ia['Commentaires sur les macro-vulnérabilités - Instabilité'] = app_json['ssi_vulnerabilites_instabilite_commentaires']
        if app_json.get('ssi_vulnerabilites_authentification_id'):
            app_ia['Macro-vulnérabilités - Authentification'] = app_json['ssi_vulnerabilites_authentification_id']
        if app_json.get('ssi_vulnerabilites_authentification_commentaires'):
            app_ia['Commentaires sur les macro-vulnérabilités - Authentification'] = app_json['ssi_vulnerabilites_authentification_commentaires']
        if app_json.get('ssi_vulnerabilites_sensibilisation_id'):
            app_ia['Macro-vulnérabilités - Sensibilisation'] = app_json['ssi_vulnerabilites_sensibilisation_id']
        if app_json.get('ssi_vulnerabilites_sensibilisation_commentaires'):
            app_ia['Commentaires sur les macro-vulnérabilités - Sensibilisation'] = app_json['ssi_vulnerabilites_sensibilisation_commentaires']
        if app_json.get('ssi_vulnerabilites_detteTechnique_id'):
            app_ia['Macro-vulnérabilités - Dette technique'] = app_json['ssi_vulnerabilites_detteTechnique_id']
        if app_json.get('ssi_vulnerabilites_detteTechnique_commentaires'):
            app_ia['Commentaires sur les macro-vulnérabilités - Dette technique'] = app_json['ssi_vulnerabilites_detteTechnique_commentaires']
        if app_json.get('ssi_vulnerabilites_hebergement_id'):
            app_ia['Macro-vulnérabilités - Hébergement'] = app_json['ssi_vulnerabilites_hebergement_id']
        if app_json.get('ssi_vulnerabilites_hebergement_commentaires'):
            app_ia['Commentaires sur les macro-vulnérabilités - Hébergement'] = app_json['ssi_vulnerabilites_hebergement_commentaires']
        if app_json.get('ssi_vulnerabilites_sousTraitance_id'):
            app_ia['Macro-vulnérabilités - Sous-traitance'] = app_json['ssi_vulnerabilites_sousTraitance_id']
        if app_json.get('ssi_vulnerabilites_sousTraitance_commentaires'):
            app_ia['Commentaires sur les macro-vulnérabilités - Sous-traitance'] = app_json['ssi_vulnerabilites_sousTraitance_commentaires']
        if app_json.get('ssi_contacts'):
            obj_list = []
            for contact in app_json['ssi_contacts']:
                obj_dict = {}
                if contact.get('roleContact_id'):
                    obj_dict['Rôle de contact'] = self.get_enumeration_name('TypeRoleContact', contact['roleContact_id'])
                if contact.get('contact_desc'):
                    obj_dict['Contact'] = contact['contact_desc']
                if contact.get('courriel'):
                    obj_dict['Courriel'] = contact['courriel']
                if contact.get('commentaire'):
                    obj_dict['Commentaire'] = contact['commentaire']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Contacts SSI'] = obj_list
        if app_json.get('arch_referentiel'):
            obj_list = []
            for referentiel in app_json['arch_referentiel']:
                obj_dict = {}
                if referentiel.get('typologie'):
                    obj_dict['Typologie'] = referentiel['typologie']
                if referentiel.get('dua'):
                    obj_dict['DUA'] = 'sans limite' if referentiel.get('dua') == 999 else '1 an' if referentiel.get('dua') == 1 else '{} ans'.format(referentiel.get('dua'))
                if referentiel.get('sortFinal_id'):
                    obj_dict['Sort final'] = self.get_enumeration_name('Arch_SortFinal', referentiel['sortFinal_id'])
                if referentiel.get('justifRegl'):
                    obj_dict['Justification réglementaire'] = referentiel['justifRegl']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Cycle de vie des documents et des données'] = obj_list
        if app_json.get('arch_criticite_id'):
            app_ia['Criticité en terme d\'archivage'] = self.get_enumeration_name('Arch_Criticite', app_json['arch_criticite_id'])
        if app_json.get('arch_diagnostic'):
            app_ia['Archivage - diagnostic'] = app_json['arch_diagnostic']
        if app_json.get('arch_action_id'):
            app_ia['Archivage - action à mener'] = self.get_enumeration_name('Arch_Action', app_json['arch_action_id'])
        if app_json.get('evolutionTechnologique') is not None:
            app_ia['Évolution technologique'] = 'oui' if app_json.get('evolutionTechnologique') == True else 'non' if app_json.get('evolutionTechnologique') == False else None
        if app_json.get('evolutionContenu') is not None:
            app_ia['Évolution du contenu'] = 'oui' if app_json.get('evolutionContenu') == True else 'non' if app_json.get('evolutionContenu') == False else None
        if app_json.get('evolutionConditionsAcces') is not None:
            app_ia['Évolution des conditions d\'accès'] = 'oui' if app_json.get('evolutionConditionsAcces') == True else 'non' if app_json.get('evolutionConditionsAcces') == False else None
        if app_json.get('evolutionUsage') is not None:
            app_ia['Évolution de l\'usage'] = 'oui' if app_json.get('evolutionUsage') == True else 'non' if app_json.get('evolutionUsage') == False else None
        if app_json.get('evolutions_precisions'):
            app_ia['Précisions sur les évolutions'] = app_json['evolutions_precisions']
        if app_json.get('contacts'):
            obj_list = []
            for contact in app_json['contacts']:
                obj_dict = {}
                if contact.get('roleContact_id'):
                    obj_dict['Rôle de contact'] = self.get_enumeration_name('TypeRoleContact', contact['roleContact_id'])
                if contact.get('contact_desc'):
                    obj_dict['Contact'] = contact['contact_desc']
                if contact.get('courriel'):
                    obj_dict['Courriel'] = contact['courriel']
                if contact.get('notification_maj') is not None:
                    obj_dict['notification_maj'] = contact['notification_maj']
                if obj_dict:
                    obj_list.append(obj_dict)
            if obj_list:
                app_ia['Contacts'] = obj_list
        if app_json.get('creationFiche'):
            app_ia['Date et heure de création de la fiche'] = app_json['creationFiche']
        if app_json.get('modificationFiche'):
            app_ia['Date et heure de modification de la fiche'] = app_json['modificationFiche']
        return app_ia

    def generate_applications_ia_mini_list(self, applications_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Génère une forme "textuelle" de l\'objet Application sans les champs vides adaptée à l\'entraînement d\'une IA.
        """
        applicationsIA_mini_list = []
        for application in applications_list:
            app_ia = self.generate_application_ia_mini(application)
            applicationsIA_mini_list.append(app_ia)
        return applicationsIA_mini_list

    def save_applications_ia_mini_list(self, applications_list: List[Dict[str, Any]]):
        """
        Sauve dans un fichier applicationsIA_mini.json les objets "textuels" sans champs vides des objets Application du wiki SI.
        """
        fileName = self.output_dir / self.config['output']['applications_ia_mini_file']
        app_ia_mini_list = self.generate_applications_ia_mini_list(applications_list)
        data = {
            'applicationsIA_mini': app_ia_mini_list
        }
        # Nettoyer les caractères Unicode problématiques avant la sauvegarde
        cleaned_data = clean_unicode_separators(data)
        with open(fileName, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=3)
        logger.info(f"Fichier '{fileName}' construit et chargé.")

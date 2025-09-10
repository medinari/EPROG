from Bio import Entrez, SeqIO
from BioSQL import BioSeqDatabase
import sqlite3

# Konfiguration
sqlite_db_path = "biosql.db"
bio_db_name = "bio_db"
Entrez.email = "your_email@example.com"

# Verbindung zur BioSQL-Datenbank
try:
    server = BioSeqDatabase.open_database(driver="sqlite3", db=sqlite_db_path)
    db = server.new_database(bio_db_name) if bio_db_name not in server else server[bio_db_name]
except sqlite3.OperationalError as e:
    print(f"Fehler beim Verbinden mit der Datenbank: {e}")
    exit()

def fetch_and_store_sequences(search_term, max_results=5):
    """Lädt Sequenzen von Entrez und speichert sie in der BioSQL-Datenbank."""
    handle = Entrez.esearch(db="nucleotide", term=search_term, retmax=max_results)
    search_results = Entrez.read(handle)
    handle.close()

    if not search_results['IdList']:
        print(f"Keine Sequenzen gefunden für den Suchbegriff: {search_term}")
        return

    for seq_id in search_results['IdList']:
        try:
            fetch_handle = Entrez.efetch(db="nucleotide", id=seq_id, rettype="gb", retmode="text")
            print(fetch_handle)
            seq_record = SeqIO.read(fetch_handle, "genbank")
            fetch_handle.close()
            db.load([seq_record]) # Speichert in die Datenbank
            print(f"Gespeichert: {seq_record.id}")
        except Exception as e:
            print(f"Fehler bei ID {seq_id}: {e}")

    server.commit()
    print("Alle Sequenzen wurden gespeichert.")

def list_sequences():
    """Zeigt alle gespeicherten Sequenzen an."""
    for record in db.values():
        print(f"ID: {record.id}, Länge: {len(record.seq)}, Beschreibung: {record.description}")


try:
    fetch_and_store_sequences("IL3[Gene]", max_results=5)
    list_sequences()
except Exception as e:
    print(f"Fehler: {e}")
finally:
    server.close()
    print("Datenbankverbindung geschlossen.")

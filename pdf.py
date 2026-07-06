import streamlit as st
import fitz  # PyMuPDF
import re
import os
import tempfile
import zipfile
import io
import pytesseract
from PIL import Image
import sqlite3
import datetime
import urllib.parse

# --- CONFIGURATION & USERS DATA ---
st.set_page_config(page_title="AuTo Split",
                    page_icon="📄", 
                    layout="centered",
                    menu_items={
                        'About': "Developed by Pranav Vedula | Department of CSE | Aditya University © 2026"
                    },
                    )

# The list of users provided to populate the SQLite database initially
INITIAL_USERS = [
    ("Dr.T.Sudha Rani", "sudharani.tirukoti@adityauniversity.in", "Sudha@123"),
    ("Dr.K.Chandra Sekhar", "chandrasekhark@adityauniversity.in", "sekhar@123"),
    ("Dr.J.Hari", "harij@adityauniversity.in", "hari@123"),
    ("Dr.V Vaitheeshwaran", "vaitheeshwaranv@adityauniversity.in", "vaitheesh@123"),
    ("DR.JALAIAH SAIKAM", "jalaiahs@adityauniversity.in", "saikam@123"),
    ("DR. K NAGARAJU", "nagarajuk@adityauniversity.in", "nagaraju@123"),
    ("Mrs.N.Akhila", "akhila.nalla@adityauniversity.in", "akhila@123"),
    ("Mrs.K.Vydehi", "Kasichainula.Vydehi@adityauniversity.in", "vydehi@123"),
    ("Mr.M. SRINU", "srinu.marni@adityauniversity.in", "srinu@123"),
    ("Mrs.P.Srilatha", "srilatha.p@adityauniversity.in", "srilatha@123"),
    ("Mr.K.Govinda Raju", "govindaraju.kaladi@adityauniversity.in", "govinda@123"),
    ("Mr.G.Uma Mahesh", "umamaheshg@adityauniversity.in", "umamahesh@123"),
    ("Mr.U.V.Ramesh", "veerarameshu@adityauniversity.in", "ramesh@123"),
    ("Mr.G.Appala Raju", "appalarajug@adityauniversity.in", "appala@123"),
    ("Mr.P.Anil Kumar", "anilkumarp@adityauniversity.in", "anil@123"),
    ("Ms.A.Sophia", "sophiaa@adityauniversity.in", "sophia@123"),
    ("Mr.Ch.Bhanu Prakash", "bhanuprakashch@adityauniversity.in", "bhanu@123"),
    ("Mr.K.Ramesh", "rameshk@adityauniversity.in", "kramesh@123"),
    ("Mrs.R PADMA SRI", "padmasrirananki@adityauniversity.in", "padma@123"),
    ("Ms.M SUPRAJA", "suprajam@adityauniversity.in", "supraja@123"),
    ("Bh.Sai Venkata Ganesh", "svganeshb@adityauniversity.in", "ganesh@123"),
    ("Dr. K V SIVA PRASAD REDDY", "kvsivaprasadreddy@adityauniversity.in", "siva@123"),
    ("Pranav Vedula", "24b11cs355@adityauniversity.in", "1234"),
    ("Rohith P", "24b11cs356@adityauniversity.in", "12345"),
    ("P Kaveri", "24b11cs352@adityauniversity.in", "12345"),
    ("Pranav Vedula", "vedulapranav@gmail.com", "1234"),
    ("Dr.P.Subba Rao", "subbaraop@adityauniversity.in", "subbarao@123"),
    ("Ramcharan", "24b11cs371@adityauniversity.in", "1234"),
    ("Mr.M.Kalyan Ram", "kalyanram.mylavarapu@adityauniversity.in", "kalyan@123"),
    ("Mrs. B Hema Nagamani", "hnagamanib@adityauniversity.in", "hema@123"),
    ("PV","pv@gmail.com","pv@123"),
    
    # --- NEW PROCTOR FACULTY ---
    ("DR.N.VISALAKSHI", "visala.narapareddi@adityauniversity.in", "visalakshi@123"),
    ("Ms. J.SRILAKSHMI", "srilakshmij@adityauniversity.in", "srilakshmi@123"),
    ("Mr.N. SIVAKUMAR", "sivakumar.nalla@adityauniversity.in", "sivakumar@123"),
    ("Mr.RAVIKUMAR INAKOTI", "ravikumari@adityauniversity.in", "ravikumar@123"),
    ("JYOTHULA VIDYA", "vidyajyothula@adityauniversity.in", "vidya@123"),
    ("DR. T. PRABHAKARARAO", "prabhakararaot@adityauniversity.in", "prabhakar@123"),
    ("DR. M V B MURALI KRISHNA M", "muralikrishnam@adityauniversity.in", "murali@123"),
    ("DR. S RAM CHANDRA POLISETTY", "srirampolisetty@adityauniversity.in", "ramchandra@123"),
    ("DR. V V KAMESH", "venkatakamesh.vinjamuri@adityauniversity.in", "kamesh@123"),
    ("Mr. K RAJENDRA", "rajendrak@adityauniversity.in", "rajendra@123"),
    ("Mr. K NAGA SIVA VARA PRASAD", "nagasivak@adityauniversity.in", "siva@123"),
    ("DR. SINDHU B", "sindhub@adityauniversity.in", "sindhu@123"),
    ("DR.APPAWALA JAYANTHI", "jayanthia@adityauniversity.in", "jayanthi@123")
]

PROCTOR_RANGES = {
    "umamaheshg@adityauniversity.in": ("24B11CS001", "24B11CS030"),
    "kvsivaprasadreddy@adityauniversity.in": ("24B11CS032", "24B11CS062"),
    "visalakshin@adityauniversity.in": ("24B11CS063", "24B11CS092"),
    "srilakshmij@adityauniversity.in": ("24B11CS093", "24B11CS122"),
    "srinu.marni@adityauniversity.in": ("24B11CS123", "24B11CS152"),
    "sivakumarn@adityauniversity.in": ("24B11CS154", "24B11CS183"),
    "ravikumar.inakoti@adityauniversity.in": ("24B11CS184", "24B11CS213"),
    "veerarameshu@adityauniversity.in": ("24B11CS214", "24B11CS244"),
    "vidyaj@adityauniversity.in": ("24B11CS245", "24B11CS275"),
    "padmasrirananki@adityauniversity.in": ("24B11CS276", "24B11CS305"),
    "kalyanram.mylavarapu@adityauniversity.in": ("24B11CS306", "24B11CS335"),
    "prabhakararaot@adityauniversity.in": ("24B11CS336", "24B11CS365"),
    "Kasichainula.Vydehi@adityauniversity.in": ("24B11CS366", "24B11CS396"),
    "muralikrishnam@adityauniversity.in": ("24B11CS397", "24B11CS426"),
    "ramchandrapolisetty@adityauniversity.in": ("24B11CS427", "24B11CS456"),
    "kameshv@adityauniversity.in": ("24B11CS457", "24B11CS486"),
    "rajendrak@adityauniversity.in": ("24B11CS487", "24B11CS517"),
    "nagasivak@adityauniversity.in": ("24B11CS518", "24B11CS548"),
    "sudharani.tirukoti@adityauniversity.in": ("25B21CS001", "25B21CS030"),
    "sindhub@adityauniversity.in": ("25B21CS031", "25B21CS061"),
    "jayanthia@adityauniversity.in": ("25B21CS062", "25B61CS002")
}

DB_NAME = "autosplit.db"
WEEKLY_LIMIT = 10

# --- BUILT-IN STUDENT DATA ---
STUDENT_DATA = {
    "24B11CS001": {"name": "AAWESH KUMAR DAS", "phone": "8603342910"},
    "24B11CS002": {"name": "ABHINAY PEDDAPATI", "phone": "8978601805"},
    "24B11CS003": {"name": "ACHI AKASH", "phone": "6305580352"},
    "24B11CS004": {"name": "ADDAGARLA LEHITHA", "phone": "7670875549"},
    "24B11CS005": {"name": "ADHIKARI DURGA MEGHANA", "phone": "8985074534"},
    "24B11CS006": {"name": "ADIGARLA SOMESWARA MANIKANTA KUMAR", "phone": "9676976417"},
    "24B11CS007": {"name": "AKKINA VAMSI DURGA", "phone": "9502746325"},
    "24B11CS008": {"name": "AKULA DEVI KUSUMA", "phone": "8501850378"},
    "24B11CS009": {"name": "AKUMARTHI SRIJA", "phone": "9949585337"},
    "24B11CS010": {"name": "ALAPATI KAVYA SRI", "phone": "9848573418"},
    "24B11CS011": {"name": "AMALADASU PRAVALLIKA", "phone": "9160612354"},
    "24B11CS012": {"name": "AMIREDDY VARSHITHA REDDY", "phone": "7207204282"},
    "24B11CS013": {"name": "AMULOJU JASWANTH KUMAR", "phone": "7659029278"},
    "24B11CS014": {"name": "DUKKA VINODKUMAR", "phone": "8978647413"},
    "24B11CS015": {"name": "ANDRU HEMANTHA VARSHA", "phone": "7989712548"},
    "24B11CS016": {"name": "ANKAM BRAHMESWARI SAI SUPRIYA", "phone": "9849737226"},
    "24B11CS017": {"name": "APPAPANTHULA CHIRANJEEVI KUMAR", "phone": "9000566601"},
    "24B11CS018": {"name": "ARAJYULA CHARAN VINAY MANIKANTA", "phone": "9848434735"},
    "24B11CS019": {"name": "ARIGELA RAJU", "phone": "9121778125"},
    "24B11CS020": {"name": "ARPAN MANDAL", "phone": "6301313372"},
    "24B11CS021": {"name": "ARUGULA PRUDVI VANI", "phone": "9381482115"},
    "24B11CS022": {"name": "BOMMALI BALA VAMSI KRISHNA PRASAD", "phone": "6301852279"},
    "24B11CS023": {"name": "BOLLINENI VENKATA SAI MANIKANTA", "phone": "9031431439"},
    "24B11CS024": {"name": "BATCHU VENKATA PREM VIVEK", "phone": "9849837981"},
    "24B11CS025": {"name": "BADDI VENKATA SRUTHI", "phone": "8096209833"},
    "24B11CS026": {"name": "BADANA SINIHA", "phone": "9849557462"},
    "24B11CS027": {"name": "BALABHADRA CHAITANYA SATYA KISHORE", "phone": "9848535992"},
    "24B11CS028": {"name": "BALAM JOHN REVIWAL", "phone": "7981683584"},
    "24B11CS029": {"name": "KARUPOTHU CHANDRIKA", "phone": "9441906509"},
    "24B11CS030": {"name": "BAMMIDI HARISH", "phone": "6281741704"},
    "24B11CS032": {"name": "BANDARU LAKSHMANA VEERA PRASAD", "phone": "9014070046"},
    "24B11CS033": {"name": "BANDARU MOHAN KUMAR", "phone": "6303663284"},
    "24B11CS034": {"name": "BANDI HARSHAVARDHAN", "phone": "9398741751"},
    "24B11CS035": {"name": "BANDI LALITHA SATYA SWAROOPA", "phone": "8499013199"},
    "24B11CS036": {"name": "BARA JEEVAN MANOJ SAI", "phone": "9618974280"},
    "24B11CS037": {"name": "BARRI VEERA VASANTHA LAKSHMI", "phone": "7396867553"},
    "24B11CS038": {"name": "BASA SRI BHAVANI SATYA SAI NIHARIKA", "phone": "9705655750"},
    "24B11CS039": {"name": "BASWANI DEEVENA", "phone": "7981949480"},
    "24B11CS040": {"name": "BATHULA DEEPTHI VARSHA", "phone": "9493288346"},
    "24B11CS041": {"name": "BATHULA SURENDRA", "phone": "9491466800"},
    "24B11CS042": {"name": "BESTHA TARUN KUMAR", "phone": "9912151855"},
    "24B11CS043": {"name": "BIKKINA VEERA VENKATA BHAVYA NANDINI", "phone": "8885881345"},
    "24B11CS044": {"name": "BIRUDULA DYNAMIC NAGA LAKSHMI NARASIMHA", "phone": "9542118147"},
    "24B11CS045": {"name": "TANGELLA TEJASWI BHAVANI", "phone": "9908404090"},
    "24B11CS046": {"name": "BODANKI KARTHIKEYA", "phone": "9441432798"},
    "24B11CS047": {"name": "BODDU PAVITHRA", "phone": "9542183555"},
    "24B11CS048": {"name": "BODDUBOYINA HEMANTH", "phone": "9704623507"},
    "24B11CS049": {"name": "BODHANAPU SUHAS", "phone": "9848793938"},
    "24B11CS050": {"name": "BOGGURAMMA GARI CHAITRA", "phone": "8500339025"},
    "24B11CS051": {"name": "BOKKA SUDHEER", "phone": "9391227589"},
    "24B11CS052": {"name": "BONAGIRI MAHAVEERA VENKATA SHANMUKHI SRI", "phone": "6302016180"},
    "24B11CS053": {"name": "BONDALA PREETHI", "phone": "9866846273"},
    "24B11CS054": {"name": "BONKU HARSHAVARDHAN", "phone": "9381575590"},
    "24B11CS055": {"name": "BORRA ANKITHA", "phone": "9866245512"},
    "24B11CS056": {"name": "BOYINA VEERA VENKATA VIVEK", "phone": "9396805332"},
    "24B11CS057": {"name": "BRUMDAVANAM SRI RAMA RAVI CHARAN", "phone": "9908914602"},
    "24B11CS058": {"name": "BUDALA YAMINI", "phone": "9505688677"},
    "24B11CS059": {"name": "BUSIM GOWRI VINAY SUDHEER", "phone": "9490086663"},
    "24B11CS060": {"name": "BYREDDY SIVAGANESH", "phone": "9640969066"},
    "24B11CS061": {"name": "CHITTAPUDI SRAVANI", "phone": "9059121303"},
    "24B11CS062": {"name": "BHUKYA SAI KUMAR NAIK", "phone": "7702029910"},
    "24B11CS063": {"name": "CHALUVADI VENKATA SUDHEESH TEJA", "phone": "9640853335"},
    "24B11CS064": {"name": "CHAPA NAGENDRA", "phone": "9912167756"},
    "24B11CS065": {"name": "CHAPPA KARTHIK NOOKARAJU", "phone": "9849173986"},
    "24B11CS066": {"name": "CHATHARAJUPALLI PRAVEEN", "phone": "9441126301"},
    "24B11CS067": {"name": "CHENNAPRAGADA V N A SAI SRIKARI", "phone": "9908053452"},
    "24B11CS068": {"name": "CHETLA MANIKANTA", "phone": "9177144523"},
    "24B11CS069": {"name": "CHIKKARAJU NAGA RATNA SATYASRI", "phone": "8008431189"},
    "24B11CS070": {"name": "CHILAKA SRIHARSHINI", "phone": "7989332114"},
    "24B11CS071": {"name": "CHILUKOTI SASI KANTH", "phone": "9963667273"},
    "24B11CS072": {"name": "CHINKARLA VISHNU", "phone": "9440166593"},
    "24B11CS073": {"name": "CHINTA HASINI DIVYA TEJASWANI", "phone": "9963740344"},
    "24B11CS074": {"name": "CHINTA NITHYA SRI", "phone": "9849796423"},
    "24B11CS075": {"name": "NALLAMILLI RAMA CHARAN REDDY", "phone": "9949337999"},
    "24B11CS076": {"name": "CHINTADA HARIKRISHNA", "phone": "8886209577"},
    "24B11CS077": {"name": "CHINTADA SASI KUMAR", "phone": "9989073072"},
    "24B11CS078": {"name": "CHINTALAPUDI JNANA SATYA RAMA VIGNESH", "phone": "8121475574"},
    "24B11CS079": {"name": "CHINTALAPUDI SAI VEERA POOJITHA", "phone": "8074326847"},
    "24B11CS080": {"name": "CHINTAPALLI MANJU", "phone": "8500514885"},
    "24B11CS081": {"name": "CHITIKINA DURGA VENKATA PRASAD", "phone": "9908542059"},
    "24B11CS082": {"name": "CHITTETI PALLAVI", "phone": "9951150572"},
    "24B11CS083": {"name": "CHITTIMENU DHANUSH SRI GOVINDA YADAV", "phone": "9492258751"},
    "24B11CS084": {"name": "CHITTURI HARINI SRI ANUSHA", "phone": "9121864654"},
    "24B11CS085": {"name": "CHOWDAM LAHARI", "phone": "9440201749"},
    "24B11CS086": {"name": "CHUKKA LAVANYA", "phone": "9573219857"},
    "24B11CS087": {"name": "FUMHANDA LAUD", "phone": "2637851233"},
    "24B11CS088": {"name": "DEGALA HARI VENKATA SATYA AYYAPA SWAMY", "phone": "9989242834"},
    "24B11CS089": {"name": "DURIPUDI SAI DURGA", "phone": "9492256678"},
    "24B11CS090": {"name": "DANDA SURYA SUDEEP", "phone": "9494159507"},
    "24B11CS091": {"name": "DANGETI BHARGAVI SAI DURGA", "phone": "9848549552"},
    "24B11CS092": {"name": "DANGETI HARSHA", "phone": "9866593822"},
    "24B11CS093": {"name": "PONNAM VIJAY KRISHNA", "phone": "9703344069"},
    "24B11CS094": {"name": "DASARI GAYATHRI", "phone": "7386174057"},
    "24B11CS095": {"name": "DASARI HEMA HARSHINI", "phone": "9676644036"},
    "24B11CS096": {"name": "DASARI HEMANTH KUMAR", "phone": "9494147096"},
    "24B11CS097": {"name": "DASARI PANDU RANGARAO", "phone": "9948226179"},
    "24B11CS098": {"name": "DASARI SIRISHA", "phone": "9440175267"},
    "24B11CS099": {"name": "DEEKSHITULA BALA SRI SWARNA PAVAN SATWIK", "phone": "9666200336"},
    "24B11CS100": {"name": "DESABATHULA MANISHA", "phone": "9951213975"},
    "24B11CS101": {"name": "DEVARAKONDA JAYANTH", "phone": "6300003846"},
    "24B11CS102": {"name": "DEVARAKONDA NAGENDRA KRISHNA MOHAN", "phone": "9948799157"},
    "24B11CS103": {"name": "DIYYA BHAVISHYA", "phone": "9491417485"},
    "24B11CS104": {"name": "DODLA VAMSI KRISHNA", "phone": "9866456624"},
    "24B11CS105": {"name": "DOGGA JASHUVA KUMAR NAIDU", "phone": "7989046300"},
    "24B11CS106": {"name": "DOKKA JAHNAVI", "phone": "9491957078"},
    "24B11CS107": {"name": "DONDA NAVYA SRI", "phone": "9491069819"},
    "24B11CS108": {"name": "CHINTHAMREDDY SUSHMA REDDY", "phone": "9440459930"},
    "24B11CS109": {"name": "THURAKA VENKATA KUMAR", "phone": "6305140524"},
    "24B11CS110": {"name": "DUDEKULA DHANUSH", "phone": "7893710483"},
    "24B11CS111": {"name": "ANURAG DUDI", "phone": "8008185444"},
    "24B11CS112": {"name": "DUNGALA KALYANI", "phone": "9618468678"},
    "24B11CS113": {"name": "DUPPALAPUDI SRI VEERA VENKATA RAMYASRUTHI", "phone": "9948256802"},
    "24B11CS114": {"name": "DWIVEDULA VENKATA SATYA SAMRUDH", "phone": "9866808568"},
    "24B11CS115": {"name": "EDAMAKANTI DIVYA TEJA", "phone": "6304873429"},
    "24B11CS116": {"name": "EDUPUGANTI PRAGNYA SREE", "phone": "9502047111"},
    "24B11CS117": {"name": "EEDUPALLI BASHITHA LAKSHMI", "phone": "9505620877"},
    "24B11CS118": {"name": "EPANAGANDLA SUBBAN BEE", "phone": "8072372443"},
    "24B11CS119": {"name": "GOLLA JOSHITHA RANI", "phone": "9701622422"},
    "24B11CS120": {"name": "BATTU MANISH REDDY", "phone": "9010999789"},
    "24B11CS121": {"name": "GADDANGI BHARGAV RAM", "phone": "9491521455"},
    "24B11CS122": {"name": "GADE REVANTH", "phone": "9182034072"},
    "24B11CS123": {"name": "SUSHIL SHARMA", "phone": "9912022617"},
    "24B11CS124": {"name": "GALLA KIRANMAI", "phone": "9951865999"},
    "24B11CS125": {"name": "GANDAM PRAVALLIKA NAGASAI", "phone": "7893560817"},
    "24B11CS126": {"name": "GANDHAM LAKSHMI PRASANNA", "phone": "7989944155"},
    "24B11CS127": {"name": "GANGORI KRISHNAKALA", "phone": "7013161224"},
    "24B11CS128": {"name": "GANTA RAJA SHEKAR", "phone": "9014204693"},
    "24B11CS129": {"name": "GARAGA PUSHPA LAKSHMI PARVATHI", "phone": "9492228909"},
    "24B11CS130": {"name": "GARAGA VIJAYA", "phone": "9848733850"},
    "24B11CS131": {"name": "GARAPATI SURYA PRAKASH CHOWDARI", "phone": "9381785698"},
    "24B11CS132": {"name": "JAVVADI VINAY", "phone": "9059855565"},
    "24B11CS133": {"name": "GELLA SAGAR", "phone": "9866437592"},
    "24B11CS134": {"name": "GODUGU RAMJEE", "phone": "9110535868"},
    "24B11CS135": {"name": "GOGIREDDY SAGAR REDDY", "phone": "9014484100"},
    "24B11CS136": {"name": "GOGULAMANDA SAMEERA", "phone": "9010656241"},
    "24B11CS137": {"name": "GOGULAPATI JAYA SAI SRUJITH RAJ", "phone": "9908294076"},
    "24B11CS138": {"name": "GOLUGURI ROOPIKA", "phone": "9154150299"},
    "24B11CS139": {"name": "GONDESI LAKSHMI HASINI REDDY", "phone": "9705804560"},
    "24B11CS140": {"name": "GOPALA KRISHNAN GOPIKA DARSHINI", "phone": "9505018225"},
    "24B11CS141": {"name": "GORREMUTCHU ANJUCHARAN", "phone": "9642798927"},
    "24B11CS142": {"name": "GORRIPAATI NAIDU", "phone": "8341812193"},
    "24B11CS143": {"name": "GOTTAPU MAHANTH SAI KUMAR", "phone": "9949487870"},
    "24B11CS144": {"name": "GOWTHU MANASWI", "phone": "9949430187"},
    "24B11CS145": {"name": "GUBBALA SYAMALA", "phone": "9398001161"},
    "24B11CS146": {"name": "GUDUPU YAMINI", "phone": "9959671921"},
    "24B11CS147": {"name": "GUNA SRI RAJENDRA REDDY PAPPU", "phone": "9542713444"},
    "24B11CS148": {"name": "GUNNABATHULA SURYA DILEEP", "phone": "9848664468"},
    "24B11CS149": {"name": "GUNTURU YASWANTH SRI SAI CHARAN", "phone": "9059057707"},
    "24B11CS150": {"name": "GURAJARAPU NANDHINI", "phone": "9951677508"},
    "24B11CS151": {"name": "GURALA LALITHADITYA BULLI SRI AMRUTHA", "phone": "7989005729"},
    "24B11CS152": {"name": "GURRAM CHENCHU TARUN", "phone": "9160187087"},
    "24B11CS154": {"name": "IPPILI LAXMAN SAI", "phone": "7569703394"},
    "24B11CS155": {"name": "ISARAPU SATISH", "phone": "9493492735"},
    "24B11CS156": {"name": "ITHADI HARSHIL PREETHAM", "phone": "9010795595"},
    "24B11CS157": {"name": "ITTE JOEL", "phone": "9849150080"},
    "24B11CS158": {"name": "JADDU LEELA KRISHNA", "phone": "7993583156"},
    "24B11CS159": {"name": "JAJIMOGGALA DEVASISH VENKAT SAI", "phone": "9912890602"},
    "24B11CS160": {"name": "JANGALA SRI RAJ KUMAR", "phone": "8639422852"},
    "24B11CS161": {"name": "JANNI PRANADEEP KUMAR", "phone": "9440877839"},
    "24B11CS162": {"name": "JERRIPOTHULA LAKSHMI SRINIVAS", "phone": "9396969626"},
    "24B11CS163": {"name": "JOGI LAKSHMANA SWAMY", "phone": "7095002249"},
    "24B11CS164": {"name": "KAKARLAPUDI MAHENDRA VARMA", "phone": "9550735199"},
    "24B11CS165": {"name": "BIGAL DAHAL", "phone": "9851061643"},
    "24B11CS166": {"name": "KOVVURI SAI DURGA PRASAD REDDY", "phone": "9951595799"},
    "24B11CS167": {"name": "KAVITAPU SAI SRINIVAS", "phone": "9492394297"},
    "24B11CS168": {"name": "KOTIKALAPUDI LEELA SATYA SRI LAKSHMI", "phone": "9949135127"},
    "24B11CS169": {"name": "KADIMI RITWIK", "phone": "9381645567"},
    "24B11CS170": {"name": "KAIRAM SATWIK SRIRAM", "phone": "9949333493"},
    "24B11CS171": {"name": "KAKARLA YASWANTH", "phone": "9618144909"},
    "24B11CS172": {"name": "KAKI SUNEELA SRI VARSHA", "phone": "9866307783"},
    "24B11CS173": {"name": "KALAHASTI THANMAI", "phone": "9848433017"},
    "24B11CS174": {"name": "KALAMKURI BHANUPRAKASH", "phone": "9494196338"},
    "24B11CS175": {"name": "KALAPUREDDI SWATHI", "phone": "9951519992"},
    "24B11CS176": {"name": "KALASANI MAHENDRA VARMA", "phone": "9948344980"},
    "24B11CS177": {"name": "KALIDINDI INDUVARSHINI", "phone": "8019508267"},
    "24B11CS178": {"name": "KALNEEDI HIRAN SRI SAI", "phone": "7095691646"},
    "24B11CS179": {"name": "KAMATHAM PRATHEEK", "phone": "8074176153"},
    "24B11CS180": {"name": "KAMBALA YASHWANTH SAI", "phone": "9493953758"},
    "24B11CS181": {"name": "KANAKAM DHANA SHREE", "phone": "8885768020"},
    "24B11CS182": {"name": "KANAPARTHI MADHU KIRAN", "phone": "9391221328"},
    "24B11CS183": {"name": "KANDAPU SHANUMUKA PRIYA", "phone": "9553112123"},
    "24B11CS184": {"name": "KANDIBOYINA AKHILA", "phone": "9652883473"},
    "24B11CS185": {"name": "KANDIMALLA TEJA SIRI", "phone": "8341082333"},
    "24B11CS186": {"name": "KANDRAGUNTA RAVITEJA", "phone": "7207147770"},
    "24B11CS187": {"name": "KANDREKULA CHANIKYA", "phone": "9959445349"},
    "24B11CS188": {"name": "KANIKE RAKSHITHA", "phone": "9885646973"},
    "24B11CS189": {"name": "Kantipudi Sri Ram Venkata Karthik", "phone": "9951444479"},
    "24B11CS190": {"name": "KAPPALA KUMARI VEERA VENKATA GNANESWARI", "phone": "9393932676"},
    "24B11CS191": {"name": "KAPPALA VENKATESH", "phone": "9490474201"},
    "24B11CS192": {"name": "KAREDI MANESH", "phone": "9492915794"},
    "24B11CS193": {"name": "KARRI CHANDRA DEVIKA REDDY", "phone": "9866244457"},
    "24B11CS194": {"name": "KARRI GOPALA VENKATA SURYA SAI", "phone": "9948804053"},
    "24B11CS195": {"name": "KARRI HIMABINDU", "phone": "7995424975"},
    "24B11CS196": {"name": "KARRI JASMITHA SRI GOWRI", "phone": "9866762796"},
    "24B11CS197": {"name": "KARRI MOHAN VAMSI REDDY", "phone": "9618192610"},
    "24B11CS198": {"name": "KARUPARTHI GOWTHAM RAJ ADITYA", "phone": "9247283576"},
    "24B11CS199": {"name": "KASALA JYOTHIESH", "phone": "6301776544"},
    "24B11CS200": {"name": "KATIKALA ANUSHA", "phone": "6301305351"},
    "24B11CS201": {"name": "KATTA SAI SUSHAMNA", "phone": "6300324545"},
    "24B11CS202": {"name": "KATTULA KIRAN BABU", "phone": "9032529461"},
    "24B11CS203": {"name": "KAYALA PHANIRAM", "phone": "9848083869"},
    "24B11CS204": {"name": "KEERTHI DHANALAKSHMI", "phone": "9948643327"},
    "24B11CS205": {"name": "KELLA YUGANDHAR", "phone": "9059015830"},
    "24B11CS206": {"name": "KESAPRAGADA S S LAKSHMI MANI HASINI", "phone": "7901016867"},
    "24B11CS207": {"name": "TIMMISETTY LAVANYA", "phone": "7989798818"},
    "24B11CS208": {"name": "KODI KALYAN SANKAR", "phone": "9493046829"},
    "24B11CS209": {"name": "KODIGANTI SUBRAMANYAM", "phone": "9989979461"},
    "24B11CS210": {"name": "KOJJA RUPESH", "phone": "8978794241"},
    "24B11CS211": {"name": "KOLATI SATYA", "phone": "9553496200"},
    "24B11CS212": {"name": "KOLE RAMADEVI", "phone": "9966729104"},
    "24B11CS213": {"name": "KOLIKI MURALI KRISHNA", "phone": "8074510066"},
    "24B11CS214": {"name": "KOLLA TRISHA", "phone": "8897714134"},
    "24B11CS215": {"name": "KOLLAPU RISHMA", "phone": "9666361973"},
    "24B11CS216": {"name": "KOMALI DURGA SAI RAJ", "phone": "9492664322"},
    "24B11CS217": {"name": "KONA BALARAJU", "phone": "8179094207"},
    "24B11CS218": {"name": "KONAGALLA SRAVANI", "phone": "8500632710"},
    "24B11CS219": {"name": "KONDA LAKSHMI MAHITH", "phone": "9550049030"},
    "24B11CS220": {"name": "KONDAPALLI SAI TEJA", "phone": "8985985288"},
    "24B11CS221": {"name": "KONDEPUDI JYOTSHNA", "phone": "9000621982"},
    "24B11CS222": {"name": "KONDASANI SOHAN KARTHIKEYA", "phone": "8008916789"},
    "24B11CS223": {"name": "KONIKINENI CHARAN TEJA", "phone": "9618525553"},
    "24B11CS224": {"name": "PILLI DURGA MOUNIKA", "phone": "9398092848"},
    "24B11CS225": {"name": "KONNIPATI JOHN", "phone": "9490369877"},
    "24B11CS226": {"name": "KOPPINEEDI SUDHA RANI", "phone": "8897014127"},
    "24B11CS228": {"name": "KOTA DEAR SUBRAHMANYAM", "phone": "9014401156"},
    "24B11CS229": {"name": "KOTHACHERUVU MAMATHA", "phone": "9701389972"},
    "24B11CS230": {"name": "KOTHALA HEMANTH", "phone": "8367564099"},
    "24B11CS231": {"name": "KOTIPALLI LAKSHMI TANAY TRIDHAMN KUMAR", "phone": "9392431461"},
    "24B11CS232": {"name": "KOTTU SAI VARSHINI", "phone": "9490850667"},
    "24B11CS233": {"name": "KOVVURI RAMAKRISHNA REDDY", "phone": "9502599745"},
    "24B11CS234": {"name": "KOYYA BALA ANU SRI", "phone": "9989517089"},
    "24B11CS235": {"name": "KOYYANA SRIVALLI", "phone": "9908888073"},
    "24B11CS236": {"name": "SANDAKA KRISHNA BHARADWAJ", "phone": "9848834493"},
    "24B11CS237": {"name": "KRISHNAM HARSHA VARDHAN", "phone": "9550066872"},
    "24B11CS238": {"name": "KUCHIMANCHI NAGA SAI LAKSHMI SAHITHI", "phone": "9346699998"},
    "24B11CS239": {"name": "KUDUPUDI SANDHYA", "phone": "9959478099"},
    "24B11CS240": {"name": "KULLU ROSHAN", "phone": "9000349054"},
    "24B11CS241": {"name": "KUNUTHURU HEMANTH KUMAR", "phone": "9492749947"},
    "24B11CS242": {"name": "KUPPALA SATYA VENKATALAKSHMI SRI SAHITHYA", "phone": "9441292999"},
    "24B11CS243": {"name": "KURRU MURARI VENKATA DURGA", "phone": "9346104420"},
    "24B11CS244": {"name": "KURUMOJU CHANDAN SONI", "phone": "8839494382"},
    "24B11CS245": {"name": "TUMMALA SATWIK", "phone": "9848851993"},
    "24B11CS246": {"name": "L PREMCHAND", "phone": "8919890120"},
    "24B11CS247": {"name": "LAKKOJU NIKHITHA DEVI", "phone": "9032866628"},
    "24B11CS248": {"name": "LALAM HIMA RAMA TEJA", "phone": "8074101499"},
    "24B11CS249": {"name": "LANKA VENKATA DURGA", "phone": "8328493978"},
    "24B11CS250": {"name": "LINGAM MANIKANTA VEERA SAI KRISHNA MANOHAR", "phone": "9948395111"},
    "24B11CS251": {"name": "LOLLA VEERENDRA", "phone": "9494300985"},
    "24B11CS252": {"name": "LUKALAPU SHARMILA", "phone": "8317507725"},
    "24B11CS253": {"name": "MAHALAXMI MACHINA", "phone": "9912816281"},
    "24B11CS254": {"name": "MOSURI NANDINI", "phone": "8978810922"},
    "24B11CS255": {"name": "M PAVAN KUMAR", "phone": "9492071451"},
    "24B11CS256": {"name": "MANGAM UMA RAM CHARAN", "phone": "7702015486"},
    "24B11CS257": {"name": "MEDAPATI MANI BHEEMESWARA REDDY", "phone": "9491436497"},
    "24B11CS258": {"name": "MACHA VIVEK", "phone": "8767488359"},
    "24B11CS259": {"name": "MADEM VENKATA BHARADWAJ", "phone": "9949912279"},
    "24B11CS260": {"name": "MAJJI BHAVANA", "phone": "8790398678"},
    "24B11CS261": {"name": "MALAGONDA HAREESH", "phone": "7672088691"},
    "24B11CS262": {"name": "MALAKALA YUVA NIRMALA NIKHILESWAR", "phone": "9705250155"},
    "24B11CS263": {"name": "MALLADI SIMHADRI", "phone": "9542620001"},
    "24B11CS264": {"name": "MALLADI SRI HARINI", "phone": "8341144843"},
    "24B11CS265": {"name": "MALLI BHARGAV PARASURAM", "phone": "7036732680"},
    "24B11CS266": {"name": "MANEPALLI MOHITH KARTHIKEYA", "phone": "9908356996"},
    "24B11CS267": {"name": "MANIPATI NAGA ABHILASH", "phone": "8074434868"},
    "24B11CS268": {"name": "MANNURU SAI CHARISHMA", "phone": "9515949864"},
    "24B11CS269": {"name": "MARADANA AKSHAYA", "phone": "7799922133"},
    "24B11CS270": {"name": "MAROTU SATYA SURYA GANESH", "phone": "9492390176"},
    "24B11CS271": {"name": "MARTURU VENU VARDHAN", "phone": "9959794075"},
    "24B11CS273": {"name": "MATTA KARTHIKEYA", "phone": "9949598888"},
    "24B11CS274": {"name": "MEDAPATI CHETHAN SATYA VIKAS REDDY", "phone": "9563186566"},
    "24B11CS275": {"name": "MEDAPATI SATYA HARSHA VARDHAN REDDY", "phone": "9866033222"},
    "24B11CS276": {"name": "MEDE DEEKSHITHA NAVA GOPIKA", "phone": "9849071063"},
    "24B11CS277": {"name": "MEDISETTI HARI SRI", "phone": "9493737104"},
    "24B11CS278": {"name": "MEDISETTI PUNYA JNANESWARI", "phone": "9966399979"},
    "24B11CS279": {"name": "MEENAVALLI MRUDHULA SAI", "phone": "6300726668"},
    "24B11CS280": {"name": "MEESALA PRAVALLIKA", "phone": "9885266639"},
    "24B11CS281": {"name": "MOGILIGUNTA AKHIL", "phone": "8919400733"},
    "24B11CS282": {"name": "MOHAMMAD ASIF", "phone": "9951386444"},
    "24B11CS283": {"name": "MOHAMMAD RAHAMTHULLA KHAN", "phone": "9951287028"},
    "24B11CS284": {"name": "MOHAMMED ARSHAD", "phone": "9848143024"},
    "24B11CS285": {"name": "MOHAMMED MOIN", "phone": "9989176661"},
    "24B11CS286": {"name": "MONDI ESWARI AKSHAYA", "phone": "9000825747"},
    "24B11CS287": {"name": "MORTHA LIKITHA", "phone": "9959718887"},
    "24B11CS288": {"name": "MOTAMARRI CHIDHANANDA SAI KRISHNA", "phone": "9866094468"},
    "24B11CS289": {"name": "MUDAPAKA HARSHA VARDHAN", "phone": "9963496200"},
    "24B11CS290": {"name": "MUDI SRINIVASULU", "phone": "9441715183"},
    "24B11CS291": {"name": "MUDRAGADA SAI SATHWIK", "phone": "9951964206"},
    "24B11CS292": {"name": "MUGADA GAYATHRI", "phone": "9490479669"},
    "24B11CS293": {"name": "MURAMULLA KAVITHA", "phone": "7989321798"},
    "24B11CS294": {"name": "MUTTE VAMSI", "phone": "9014603316"},
    "24B11CS295": {"name": "MUTYA VENKATA SATYASAI SRIVIDYA", "phone": "9908914015"},
    "24B11CS296": {"name": "NANDAMURI HARI VEERA NAGA CHARAN", "phone": "9676781189"},
    "24B11CS297": {"name": "NAGOJU LAKSHMI CHENDRIKA", "phone": "8897333800"},
    "24B11CS298": {"name": "NADAPANA SIVA SRI", "phone": "9989366952"},
    "24B11CS299": {"name": "NADIMINTI DHANUNJAYA RAO", "phone": "6305639374"},
    "24B11CS300": {"name": "NAGADASARI SANTHOSH KUMAR", "phone": "7032607135"},
    "24B11CS301": {"name": "NAGAGAYATHRI YEDLA", "phone": "8317686342"},
    "24B11CS302": {"name": "NAGATHOTA STUTI PAULIN MILTON", "phone": "9110796832"},
    "24B11CS303": {"name": "NAGAVARAPU SAI SRAVYA", "phone": "9030242547"},
    "24B11CS304": {"name": "RAMINEEDI VENKATA SRI SAI PHANI NEELESH", "phone": "8500800849"},
    "24B11CS305": {"name": "NAIDU KEERTHI NAGA MAHA LAKSHMI", "phone": "8897057972"},
    "24B11CS306": {"name": "NAKKA JASWANTH NARAYANA", "phone": "9848623557"},
    "24B11CS307": {"name": "NAKKA KIRAN SAI RAJ KUMAR", "phone": "9346676196"},
    "24B11CS308": {"name": "NALAM NAGA VENKAT SIVA RAMYA", "phone": "9885085827"},
    "24B11CS309": {"name": "NALAM NAGA VENKATA SIVA SOWMYA", "phone": "9885085827"},
    "24B11CS310": {"name": "NALLAM VENKATA NATESH", "phone": "7794052909"},
    "24B11CS311": {"name": "NALLAMILLI NAGA SRI AKSHAYA", "phone": "9849614888"},
    "24B11CS312": {"name": "NALLAMILLI SATYA SHRIYA", "phone": "9246755656"},
    "24B11CS313": {"name": "NAMALA JAGAPATHI RAMA RAO", "phone": "9603233760"},
    "24B11CS314": {"name": "NARALA VAMSI KRISHNA", "phone": "9032800706"},
    "24B11CS315": {"name": "NB AKIRANANDAN", "phone": "9739788196"},
    "24B11CS316": {"name": "NEERUKONDA THANUSHA", "phone": "9951318893"},
    "24B11CS317": {"name": "NERELLA JOTHIKA", "phone": "9492188268"},
    "24B11CS318": {"name": "NIMMAKAYALA VENKATESH", "phone": "9553629772"},
    "24B11CS319": {"name": "NOOKALA HARSHITH KRISHNA SAI", "phone": "8500132949"},
    "24B11CS320": {"name": "NUNNA BHAVYA SRI", "phone": "8121242405"},
    "24B11CS321": {"name": "NURUKURTHI NAGA VENKATA SAI HRUDAI", "phone": "9246695891"},
    "24B11CS322": {"name": "PANDALA PRASANTH KUMAR", "phone": "9866607636"},
    "24B11CS323": {"name": "PATAMSETTI SATYANARAYANA SWAMI", "phone": "9010057678"},
    "24B11CS324": {"name": "PADALA SRIRAM SIDDHARDHA REDDY", "phone": "9248148555"},
    "24B11CS325": {"name": "PADAVALA VENKATA VISHNU VARDHAN", "phone": "9848398877"},
    "24B11CS326": {"name": "PAILA VENKATI", "phone": "9989327962"},
    "24B11CS327": {"name": "PALA SRIDATTA SAI", "phone": "8501079057"},
    "24B11CS328": {"name": "CARDETTE DHLIWAYO", "phone": "776467359"},
    "24B11CS329": {"name": "PALLA SAI VEERA POOJITHA", "phone": "9866211194"},
    "24B11CS330": {"name": "VASAM SURYAMANIKANTA", "phone": "855588277"},
    "24B11CS331": {"name": "PAMPANA BALA VENKATA CHANDRA SEKHAR", "phone": "8106665429"},
    "24B11CS332": {"name": "PAMPANA CHETAN SURYA VINAY", "phone": "9676146272"},
    "24B11CS333": {"name": "PAMPARABOINA VARAMMA", "phone": "9390284010"},
    "24B11CS334": {"name": "PANDI AISWARYA", "phone": "9704568755"},
    "24B11CS335": {"name": "PANDITI JASMINE", "phone": "9515229580"},
    "24B11CS336": {"name": "PASUMARTHI SUMANTH", "phone": "9966858579"},
    "24B11CS337": {"name": "PATNALA ASRITHA SATYA", "phone": "9133838955"},
    "24B11CS338": {"name": "PECHETTI PRABHAS", "phone": "9949566589"},
    "24B11CS339": {"name": "PEMMANABOYINA TULASI", "phone": "9390307427"},
    "24B11CS340": {"name": "PENKE VEERA VENKATA AVINASH", "phone": "9290144004"},
    "24B11CS341": {"name": "PENUGONDA NAGA SUPRAJA", "phone": "9581558052"},
    "24B11CS342": {"name": "PENUMALLU SATYA HARINI", "phone": "9505411568"},
    "24B11CS343": {"name": "PEPAKAYALA BAKHT SINGH", "phone": "7016364299"},
    "24B11CS344": {"name": "PEPAKAYALA SRI SAI DURGA ROOPA LAVANYA", "phone": "9550565099"},
    "24B11CS345": {"name": "PIDUGU VENKATA KRISHNA", "phone": "939831038"},
    "24B11CS346": {"name": "PILLA DHANUSH", "phone": "9505204535"},
    "24B11CS347": {"name": "PINISETTY SATYA DURGA PRASAD", "phone": "9848664374"},
    "24B11CS348": {"name": "PITCHUKA DEVI SUPRIYA", "phone": "9573990255"},
    "24B11CS349": {"name": "PITTA MOHAN GANESH", "phone": "9948252750"},
    "24B11CS350": {"name": "PONNADA SUSMITHA MADHULIKA", "phone": "9949102169"},
    "24B11CS351": {"name": "PAPOLU LIKHITHA", "phone": "8500798073"},
    "24B11CS352": {"name": "POSA KAVERI", "phone": "6302256585"},
    "24B11CS353": {"name": "POTHURI SATYA HARSHINI", "phone": "9963745994"},
    "24B11CS354": {"name": "PRAGNYA YARAMATI", "phone": "9959235555"},
    "24B11CS355": {"name": "PRANAV VEDULA", "phone": "9701002884"},
    "24B11CS356": {"name": "PRATHIPATI ROHITH", "phone": "9989578797"},
    "24B11CS357": {"name": "PRIYAMWAD RAI", "phone": "9503504027"},
    "24B11CS358": {"name": "PRIYANSHU SARMA", "phone": "9531120322"},
    "24B11CS359": {"name": "PUJARI BHAVANA", "phone": "9030414548"},
    "24B11CS360": {"name": "PULIMEY NAGA PRUDHVIRAJ", "phone": "9603179079"},
    "24B11CS361": {"name": "PULLA LAKSHMI KALABHIRAM", "phone": "9640569888"},
    "24B11CS362": {"name": "PULUGUZZU KEERTHI DARAHAS", "phone": "9705240320"},
    "24B11CS363": {"name": "TATIKONDA ANVITH", "phone": "8885771525"},
    "24B11CS364": {"name": "PUSALA SUSHMA", "phone": "9951806214"},
    "24B11CS365": {"name": "PYLA TEJA GANESH", "phone": "9491686577"},
    "24B11CS366": {"name": "RAJABOINA TEJAS", "phone": "8341876959"},
    "24B11CS367": {"name": "RAJARAPU DHANALAKSHMI", "phone": "9908792772"},
    "24B11CS368": {"name": "RAJARAPU KARTHIK", "phone": "9848982432"},
    "24B11CS369": {"name": "RAKESH JANGA", "phone": "9963212629"},
    "24B11CS370": {"name": "RAMAKURTHI HEMANTH PRASAD", "phone": "6303045087"},
    "24B11CS371": {"name": "VASAMSETTI SRI RAM CHARAN", "phone": "9949511562"},
    "24B11CS372": {"name": "RAPARTHI VEERA VENKATA SIVA SANTHOSH KUMAR", "phone": "9966343050"},
    "24B11CS373": {"name": "RASAMSETTI HARSHA KUMAR", "phone": "9703047032"},
    "24B11CS374": {"name": "RAVULAPALLI VENKATA GOPI", "phone": "9949899197"},
    "24B11CS376": {"name": "RAYUDU BALA PRASANNA", "phone": "9618773339"},
    "24B11CS377": {"name": "REBBA ROHIT", "phone": "9666989572"},
    "24B11CS378": {"name": "REDLA LAVANYA", "phone": "9948337731"},
    "24B11CS379": {"name": "RELANGI ANAND BABU", "phone": "7287873300"},
    "24B11CS380": {"name": "KODAVANDLAPALLI LAKSHMI SREENIVAS REDDY", "phone": "9985992450"},
    "24B11CS381": {"name": "ROKKAM SURYA KIRAN", "phone": "9948288776"},
    "24B11CS382": {"name": "RONGALA LIKHITH SAI VARDHAN", "phone": "9966141136"},
    "24B11CS383": {"name": "RYALI ANUHYA", "phone": "9292355613"},
    "24B11CS384": {"name": "S TEJDEEP", "phone": "8978054651"},
    "24B11CS385": {"name": "SAVARAM THANU SREE", "phone": "7780630141"},
    "24B11CS386": {"name": "SABAKA ABHISHEK", "phone": "9963312248"},
    "24B11CS387": {"name": "SABBARAPU DIVYA", "phone": "9640516672"},
    "24B11CS388": {"name": "SABBINEEDI ANNAPURNA LAKSHMI BHAVANI", "phone": "8121419151"},
    "24B11CS389": {"name": "SADANALA SURYA NARAYANA", "phone": "9381811887"},
    "24B11CS390": {"name": "SALAGRAMA SRI NAGA VISWESWARA NARASIMHA SAKETH", "phone": "9989326449"},
    "24B11CS391": {"name": "SAMALA YASASWINI", "phone": "8341065558"},
    "24B11CS392": {"name": "SAMMINGA KANAKA DURGA KAVERI", "phone": "9949010856"},
    "24B11CS393": {"name": "SAMSANI SATYA KALYAN", "phone": "9010141151"},
    "24B11CS394": {"name": "SAPPARAPU TEJA NAGA SATYA GANESH", "phone": "9000268144"},
    "24B11CS395": {"name": "SARANTI SAISINDHU", "phone": "9550720443"},
    "24B11CS396": {"name": "SARIDE HEMANTH SRINIVAS", "phone": "9948124166"},
    "24B11CS397": {"name": "SARVASUDDI SREEVALLI", "phone": "9666460290"},
    "24B11CS398": {"name": "SATHI VIVEK REDDY", "phone": "9866011007"},
    "24B11CS399": {"name": "SATTENAPALLI BHASKAR KRISHNA", "phone": "8186063321"},
    "24B11CS400": {"name": "SATTI ANAND REDDY", "phone": "9866311996"},
    "24B11CS401": {"name": "SATTI HAMSINI", "phone": "9866693366"},
    "24B11CS402": {"name": "SATTI ROHITH VENKATA MANIKANTA REDDY", "phone": "7337010859"},
    "24B11CS403": {"name": "SAVALAM VASANTHI", "phone": "7901797934"},
    "24B11CS404": {"name": "SAVARAM REKHA VARSHINI", "phone": "8247882294"},
    "24B11CS405": {"name": "SAWANT TRISHALI", "phone": "9705433716"},
    "24B11CS406": {"name": "SEERAM VANIPRASANNA", "phone": "8985489992"},
    "24B11CS407": {"name": "SHAIK ANWAR HEENA KAUSAR", "phone": "9959459461"},
    "24B11CS408": {"name": "SHAIK FAHEEM AHAMED", "phone": "9441774510"},
    "24B11CS409": {"name": "PUTTA VISHNU VARDHAN", "phone": "7780722411"},
    "24B11CS410": {"name": "SHAIK JAHEER", "phone": "9885027317"},
    "24B11CS411": {"name": "SHAIK NOOR HAMEEDA", "phone": "9392644269"},
    "24B11CS412": {"name": "SHAIK NOORJAHAN SAMEERA", "phone": "9059991308"},
    "24B11CS413": {"name": "SHAIK RASHEEDA FATHIMA", "phone": "9640187818"},
    "24B11CS414": {"name": "SHAIK SUMAIR", "phone": "9908985028"},
    "24B11CS415": {"name": "SHAIK YASMIN", "phone": "9440935448"},
    "24B11CS416": {"name": "SIDDIREDDY SAI PRANEETHA", "phone": "9059074765"},
    "24B11CS417": {"name": "SINDEY ABHINAV", "phone": "8310162968"},
    "24B11CS418": {"name": "SINGAMPALLI LAVARAJU", "phone": "9347423851"},
    "24B11CS419": {"name": "SIVAKOTI SUGUNA", "phone": "9959555934"},
    "24B11CS420": {"name": "SOMAROUTHU SRI PADHA NIKHIL", "phone": "9849249488"},
    "24B11CS421": {"name": "SOME SAI SUSHANTH", "phone": "7981659722"},
    "24B11CS422": {"name": "PANTHAM SRI SAI SIVA NAGA RAMANI KUMARI", "phone": "9440950575"},
    "24B11CS423": {"name": "SUDARSANAM PAVANI", "phone": "9494896102"},
    "24B11CS424": {"name": "SUNKARA SRI HANUSH NANDA KUMAR", "phone": "7893391133"},
    "24B11CS425": {"name": "SURI VENKATA DURGA", "phone": "9866564378"},
    "24B11CS426": {"name": "SURUBHOTLA SANTOSH KRISHNA KUMAR", "phone": "9390975546"},
    "24B11CS427": {"name": "SUSANNA HEBZIBAH POSUPO", "phone": "9704387602"},
    "24B11CS428": {"name": "SWAYAMBHARAPU VENKATA SIVA KUMAR", "phone": "8074787313"},
    "24B11CS429": {"name": "TALATAM VIJAY KUMAR SWAMY", "phone": "9440594689"},
    "24B11CS430": {"name": "TADI BHARGAV RAM", "phone": "9849860137"},
    "24B11CS431": {"name": "TADI SATYA SRAVANI", "phone": "9866827777"},
    "24B11CS432": {"name": "TADIGADAPA SRAVANTHI", "phone": "9701998769"},
    "24B11CS433": {"name": "TALAGATURI VIVEK", "phone": "8801228894"},
    "24B11CS434": {"name": "TALATAM MANOJ KUMAR", "phone": "7396606392"},
    "24B11CS435": {"name": "TANUKU KUSUMA", "phone": "9948111863"},
    "24B11CS436": {"name": "TANUKU YAMUNA", "phone": "9948832886"},
    "24B11CS437": {"name": "THOKADA TANVI RAGA VARSHINI", "phone": "9618082885"},
    "24B11CS438": {"name": "TATAVARTHI SAI ADITHYA", "phone": "9959017592"},
    "24B11CS439": {"name": "TATAVARTHI VENKATA RAMA INDU BHARGAVI", "phone": "9849727647"},
    "24B11CS440": {"name": "CHENNABOINA PREETHI", "phone": "9515187602"},
    "24B11CS441": {"name": "TETALI SATYA NAGENDRA SRIKHAR REDDY", "phone": "9849242777"},
    "24B11CS442": {"name": "KANAKA RAKESH VARMA", "phone": "8184843110"},
    "24B11CS443": {"name": "THEVULA VENKATESH YADAV", "phone": "9652438665"},
    "24B11CS444": {"name": "THIKKISETTI VEERA VENKATA SATYANARAYANA", "phone": "9959157161"},
    "24B11CS445": {"name": "THOMMANDRU SUSANTH KUMAR", "phone": "9676265638"},
    "24B11CS446": {"name": "THOTA ARAVIND SAI KUMAR", "phone": "9949386779"},
    "24B11CS447": {"name": "THOTA DIVYESWARI DEVI", "phone": "9494003699"},
    "24B11CS448": {"name": "THOTA KALPANA", "phone": "7093485208"},
    "24B11CS449": {"name": "THOTA RAMYA", "phone": "9849284480"},
    "24B11CS450": {"name": "THOTA SARITHA", "phone": "9494855333"},
    "24B11CS451": {"name": "TIBIRISETTI MONISHA PRADYUMNA SRI", "phone": "9866960450"},
    "24B11CS452": {"name": "TIRNATI HEMALATHA", "phone": "7013054161"},
    "24B11CS453": {"name": "TIRUVAIPATI HARINI SRI VEDHA ALVAR", "phone": "8096619009"},
    "24B11CS454": {"name": "TULASI K S S AMARNATH", "phone": "9440110021"},
    "24B11CS455": {"name": "TUMMALA MANIKANTA SUBHASH", "phone": "8978923333"},
    "24B11CS456": {"name": "LAKSHMI VENKAT LOKESH MURTHY TURANGI", "phone": "9849715229"},
    "24B11CS457": {"name": "UDARAGUDI RAVI KISHORE", "phone": "9676220042"},
    "24B11CS458": {"name": "ULLIGADDALA KARTHIK", "phone": "9032218426"},
    "24B11CS459": {"name": "UNDAMATLA SRI SURYA", "phone": "9948197115"},
    "24B11CS460": {"name": "UPPARA SAIDEEPTHI", "phone": "9505879839"},
    "24B11CS461": {"name": "VISARAPU HEMA SATYA SRI", "phone": "6305843535"},
    "24B11CS462": {"name": "PAVAN SATYA PRASAD VADIPARTHI", "phone": "7794949435"},
    "24B11CS463": {"name": "VEMULA SRI VIVEK", "phone": "9948502929"},
    "24B11CS464": {"name": "VASAMSETTI VENKATA NIKHIL", "phone": "8466869233"},
    "24B11CS465": {"name": "VADDE DIVYA", "phone": "9652084119"},
    "24B11CS466": {"name": "VADDI LEELA BALAJI", "phone": "9440187545"},
    "24B11CS467": {"name": "VAJRALA VENKATA KARTHIKEYAN REDDY", "phone": "9704358360"},
    "24B11CS468": {"name": "VAKA KARTHIKA", "phone": "8500132851"},
    "24B11CS469": {"name": "VAKA PAVAN KALYAN", "phone": "7032814729"},
    "24B11CS470": {"name": "VALLAGI JOSHUVA CHAKRAVARTHY", "phone": "8019622780"},
    "24B11CS471": {"name": "SHAIK SHAROOK", "phone": "9502849533"},
    "24B11CS472": {"name": "VANAPARTHI MAHI SATYA SRIVALLI", "phone": "8464946333"},
    "24B11CS473": {"name": "KURUVA SATHEESH KUMAR", "phone": "8519883043"},
    "24B11CS474": {"name": "VANKA ADITYA", "phone": "8688755906"},
    "24B11CS475": {"name": "MUZA TAFADZWA", "phone": "773096322"},
    "24B11CS476": {"name": "VARIKUTI MAHESH", "phone": "9381266336"},
    "24B11CS477": {"name": "VARUN KUMAR POLUMURI", "phone": "7013955967"},
    "24B11CS478": {"name": "VASA PRAVALLIKA", "phone": "9010207587"},
    "24B11CS479": {"name": "VAVILAPALLI KIRAN", "phone": "6305142956"},
    "24B11CS480": {"name": "VAYYAVURU YOGESH KUMAR", "phone": "9491448825"},
    "24B11CS481": {"name": "VEERA HARI VEERA VENKAT", "phone": "9963209479"},
    "24B11CS482": {"name": "VEERA HARSHINI", "phone": "9347701163"},
    "24B11CS483": {"name": "VELAGALA SUBBIREDDY", "phone": "9246662225"},
    "24B11CS484": {"name": "VELUGUBANTI RAM CHARAN SAI", "phone": "9581579999"},
    "24B11CS485": {"name": "VENGALA BRUNDA", "phone": "8639914262"},
    "24B11CS486": {"name": "VENNAPUSA GANESH", "phone": "9391121881"},
    "24B11CS487": {"name": "VENNAVALLI NIKHITA", "phone": "9092266909"},
    "24B11CS488": {"name": "GOROGODO TAKUNDA LEONARD", "phone": "778979152"},
    "24B11CS489": {"name": "VISWAJEET", "phone": "6381214539"},
    "24B11CS490": {"name": "VITTANALA GNANASREE", "phone": "9121703648"},
    "24B11CS491": {"name": "VUDDAGIRI LAKSHMI JAHNAVI", "phone": "9666582159"},
    "24B11CS492": {"name": "VUPPALA SRI AKSHITA", "phone": "7702772617"},
    "24B11CS493": {"name": "VUTUKURU SURAJ KAUSHIK", "phone": "9182936634"},
    "24B11CS495": {"name": "YADLA AKASH", "phone": "9441327048"},
    "24B11CS496": {"name": "YALLA GLADIS ESTHER", "phone": "8106249840"},
    "24B11CS497": {"name": "YALLA RAVI PRAKASH", "phone": "9032476556"},
    "24B11CS498": {"name": "YAMALA MAHITHA", "phone": "7702844420"},
    "24B11CS499": {"name": "YAMANA MAHENDRA VIJAYA NAGA BALAJI", "phone": "7794877441"},
    "24B11CS500": {"name": "YANAMALA POORNITHA", "phone": "9492810918"},
    "24B11CS501": {"name": "YARABOLU THANUJA", "phone": "9676253595"},
    "24B11CS502": {"name": "YARLAGADDA CHANDRA KOUSHIK", "phone": "9490257857"},
    "24B11CS503": {"name": "YARRA SHANMUKHA RAM SAI", "phone": "9492419773"},
    "24B11CS504": {"name": "YARRAMSETTY PAVAN PUTRA", "phone": "9849503355"},
    "24B11CS505": {"name": "YATTAPU MENAKA", "phone": "9441880408"},
    "24B11CS506": {"name": "YELISETTI KOTESWARA RAO", "phone": "9640443272"},
    "24B11CS507": {"name": "YELISETTI PRAGNYA", "phone": "9441785808"},
    "24B11CS508": {"name": "YERRABOTHULA VARUN TEJA", "phone": "8639483342"},
    "24B11CS509": {"name": "SHAIK LATHEEF", "phone": "7569603846"},
    "24B11CS510": {"name": "YERRIBOINA VENKATA HARSHAVARDHAN", "phone": "6302658449"},
    "24B11CS511": {"name": "NYAMHAMBA BUDWELL K", "phone": "772520803"},
    "24B11CS512": {"name": "GONGATI JAHNAVI", "phone": "8247576168"},
    "24B11CS513": {"name": "SHAIK AFEEF", "phone": "9441858195"},
    "24B11CS514": {"name": "VASAMSETTI JAYA SAI KRISHNA", "phone": "9391542777"},
    "24B11CS515": {"name": "KINNERA BALU", "phone": "7780495246"},
    "24B11CS516": {"name": "UCHHUSAGARI ASRAF", "phone": "9010487715"},
    "24B11CS517": {"name": "MAHAMMAD HUSSAIN SHARIF", "phone": "9704458957"},
    "24B11CS518": {"name": "CHANDAN PRASAD GURRAM", "phone": "9989531290"},
    "24B11CS519": {"name": "GADIPUDI SRINIVASA RAOA", "phone": "9963404741"},
    "24B11CS520": {"name": "JONNADA NAGA PAVAN GANESH", "phone": "9490344387"},
    "24B11CS521": {"name": "KOLLU JYOTHI SWAROOP", "phone": "8309198987"},
    "24B11CS522": {"name": "PENUPOTULA KASI SIVA SANKAR SOMESH", "phone": "9704929411"},
    "24B11CS523": {"name": "RAVURI GREESHMANTH SAI VENKATESH", "phone": "9397905530"},
    "24B11CS524": {"name": "RONGALA JWALITHA PRIYA DARSHINI", "phone": "9908854310"},
    "24B11CS525": {"name": "TANYUMARA ELTON", "phone": "783275494"},
    "24B11CS526": {"name": "VEMULA MAHENDRA", "phone": "6305630288"},
    "24B11CS527": {"name": "SIMMA VEERAMANI VENKAT KUMAR", "phone": "9440528067"},
    "24B11CS528": {"name": "KOPPISETTI EBENEZER", "phone": "9948903933"},
    "24B11CS529": {"name": "GENDERE TANATSWA HILARY", "phone": "772839709"},
    "24B11CS530": {"name": "MUNYAWARARA TAKUDZWA MOSES", "phone": "775259867"},
    "24B11CS532": {"name": "MANGWENDE ISHEANOPAE", "phone": "772588711"},
    "24B11CS533": {"name": "LIBERATOR GWINYAI HAKUONWI TANAKA NYADUNDU", "phone": "781702550"},
    "24B11CS534": {"name": "CHINODA CATHAGE TAPIWA", "phone": "773074872"},
    "24B11CS535": {"name": "CHIPFUMO KUDZAI SEON", "phone": "772520803"},
    "24B11CS536": {"name": "CHIGUBHU TRINITY", "phone": "778273664"},
    "24B11CS537": {"name": "BLESSED ZAMBEZI", "phone": "776466423"},
    "24B11CS538": {"name": "CHINOKWETU DARLINGTON", "phone": "784838341"},
    "24B11CS539": {"name": "CHIPIMO TAKUDZWA", "phone": "787010385"},
    "24B11CS540": {"name": "RUVOKO JOYLEEN RUTENDO", "phone": "773159602"},
    "24B11CS541": {"name": "METTU ROHAN", "phone": "9912165699"},
    "24B11CS542": {"name": "KARIWO IBANOSHI", "phone": "263782031561"},
    "24B11CS543": {"name": "ANASHE AMANDA BEVERLY MHAZO", "phone": "777459408"},
    "24B11CS544": {"name": "DASAM VIJAYA", "phone": "9391648383"},
    "24B11CS545": {"name": "GALIDEVARA KUMUDINI", "phone": "9849316486"},
    "24B11CS546": {"name": "MANGWAYANA BELIEVE", "phone": "775013001"},
    "24B11CS547": {"name": "KAPANYOTA NEVER JUNIOR", "phone": "2637727244"},
    "24B11CS548": {"name": "MURINDA PRINCE T", "phone": "7997822642"},
    "25B21CS001": {"name": "KARELLA SIVALOKESH", "phone": "9618388249"},
    "25B21CS002": {"name": "NARRA NAGA SRI SAI SHASHANK", "phone": "8309347568"},
    "25B21CS003": {"name": "POTHULA DURGA SAI KRISHNA", "phone": "9640641779"},
    "25B21CS004": {"name": "KORUPROLU NAGAJYOTHIKA", "phone": "9949318725"},
    "25B21CS005": {"name": "DONKINA VEERA BHAGYESH", "phone": "9441744408"},
    "25B21CS006": {"name": "CHAITANYA SRI BALAJI PUTRA", "phone": "9949921299"},
    "25B21CS007": {"name": "UPPALAPATI MANIKANTA", "phone": "7036283688"},
    "25B21CS008": {"name": "MAMIDI JYOTHI SAI CHARAN", "phone": "6281948989"},
    "25B21CS009": {"name": "SWAMIREDDY UMA MAHESWAR", "phone": "9701655263"},
    "25B21CS010": {"name": "PUPPALA RAM KARTHIK", "phone": "8143833959"},
    "25B21CS011": {"name": "ADDANKILA LAKSHMI NARAYANA DURGA SUMANTH", "phone": "9912920797"},
    "25B21CS012": {"name": "ANISETTI NAGA VENKATA SIDDHARDHA REDDY", "phone": "9701179251"},
    "25B21CS013": {"name": "K K V D NISHANTH REDDY", "phone": "8639721056"},
    "25B21CS014": {"name": "SETTI YESHWANTH", "phone": "8096822796"},
    "25B21CS015": {"name": "KORUPROLU KAVYA MAHESWARI", "phone": "9989195993"},
    "25B21CS016": {"name": "PICHHUKA HEMANTH", "phone": "9908019987"},
    "25B21CS017": {"name": "SRI ANJAN KUMAR", "phone": "9948584856"},
    "25B21CS018": {"name": "MAJJI SYAM PRASAD", "phone": "9951862833"},
    "25B21CS019": {"name": "ANIVIREDDY ASHOK", "phone": "9381235044"},
    "25B21CS020": {"name": "ARATLA NOOKA RAJU", "phone": "7799423836"},
    "25B21CS021": {"name": "YANDAMURI MEGHAMS VILSON RAJ", "phone": "9515686689"},
    "25B21CS022": {"name": "YAGA RAMTEJ", "phone": "9963945412"},
    "25B21CS023": {"name": "PANNEERU LAKSHMI VINAYRAJU", "phone": "9951202912"},
    "25B21CS024": {"name": "CHINNI KRISHNA VELUGUBANTI", "phone": "8466896989"},
    "25B21CS025": {"name": "JAVVADI JASON", "phone": "9494968990"},
    "25B21CS026": {"name": "POLIREDDY RAMU", "phone": "9553252789"},
    "25B21CS027": {"name": "KETHA AKHIL", "phone": "9154369593"},
    "25B21CS028": {"name": "MAJJI VENKATESH", "phone": "7569216944"},
    "25B21CS029": {"name": "SRIPADA SRI HASINI", "phone": "8978615317"},
    "25B21CS030": {"name": "MANDAVELLI HARI SURYA NAGENDRA NAVEEN", "phone": "9000680070"},
    "25B21CS031": {"name": "KEDARISETTI YASHWANTH KUMAR", "phone": "9866483483"},
    "25B21CS032": {"name": "VANKA SAI AMARNADH CHOWDARY", "phone": "8712403113"},
    "25B21CS033": {"name": "PAMIDI TEJOVANTH", "phone": "9391234666"},
    "25B21CS034": {"name": "NAGIREDDY SATYA SAI GANESH", "phone": "6304623982"},
    "25B21CS035": {"name": "YELUBANDI KARTHIKESWAR", "phone": "8886740663"},
    "25B21CS036": {"name": "MADDISETTY BALAJI", "phone": "7799617619"},
    "25B21CS037": {"name": "MARELLA SRIRAM CHARAN TEJA", "phone": "9550043255"},
    "25B21CS038": {"name": "TADI VARUN SANTHOSH", "phone": "7799652237"},
    "25B21CS039": {"name": "PENDEM MAHESWARI", "phone": "8143594202"},
    "25B21CS040": {"name": "DORA SATYA SURYA VARAPRASAD", "phone": "9640636444"},
    "25B21CS041": {"name": "DULLA VAMSI", "phone": "9676119316"},
    "25B21CS042": {"name": "KOVVURI ASRITHA", "phone": "9866190278"},
    "25B21CS043": {"name": "KADIYALA SAI RAHUL RAJ", "phone": "9505556035"},
    "25B21CS044": {"name": "PEPAKAYALA BHASKARA AKHILESH", "phone": "9347188549"},
    "25B21CS045": {"name": "VALLU SRIRAMA VENKATA SATYA SURYANARAYANA", "phone": "7382435385"},
    "25B21CS046": {"name": "KURUMALLA VENKATA PAVAN", "phone": "8897941393"},
    "25B21CS047": {"name": "SYED KAMALUDDIN", "phone": "6304249944"},
    "25B21CS048": {"name": "KOTA LAKSHMI NARAYANA", "phone": "9885532279"},
    "25B21CS049": {"name": "PATTAPAGALA PRASAD", "phone": "8328073049"},
    "25B21CS050": {"name": "BODEM RUPA SREE", "phone": "9866959604"},
    "25B21CS051": {"name": "DEVARAKONDA RADHA KRISHNA", "phone": "9849967648"},
    "25B21CS052": {"name": "KAREDLA DURGA SREE VEERA MANIKANTA", "phone": "9949799629"},
    "25B21CS053": {"name": "MADDIPATI MANIKANTA", "phone": "9347779313"},
    "25B21CS054": {"name": "CHIKKALA SURYA TEJA", "phone": "9505647389"},
    "25B21CS055": {"name": "KONA NIKHITA GRACE", "phone": "9652324999"},
    "25B21CS056": {"name": "ALETI SOMA SEKHAR DEEPAK", "phone": "9493865761"},
    "25B21CS057": {"name": "OLETI DILIP KISHORE", "phone": "9848581079"},
    "25B21CS058": {"name": "BADE SEKHAR", "phone": "9676449763"},
    "25B21CS059": {"name": "ANYAM ADHI BABU", "phone": "9553491444"},
    "25B21CS060": {"name": "BOTSA HARI MANIKANTA RAJ", "phone": "9704082077"},
    "25B21CS061": {"name": "VAIBOGULA LOKESH DURGA ANIL", "phone": "9912273967"},
    "25B21CS062": {"name": "DANGETI AJAY KUMAR", "phone": "9515799978"},
    "25B21CS063": {"name": "KAPILESWARAPU TEJASRI", "phone": "9908423653"},
    "25B21CS064": {"name": "YANDAM TANUJA", "phone": "7799482200"},
    "25B21CS065": {"name": "KANCHI CHANDRA MOULI", "phone": "8333951505"},
    "25B21CS066": {"name": "BALABHADRUNI LAKSHMI VEERA SURYA PRAKASH", "phone": "9603898318"},
    "25B21CS067": {"name": "KONDAPALLI VENKATA RAO", "phone": "9704804988"},
    "25B21CS068": {"name": "CHINNAM MANOJ", "phone": "8985076173"},
    "25B21CS069": {"name": "PAILA VENKATA LAKSHMI", "phone": "9550874040"},
    "25B21CS070": {"name": "TALLA NAGA SAI CHARAN", "phone": "7842791603"},
    "25B21CS071": {"name": "ARATAKATLA HEMANTH SIVA KUMAR", "phone": "6301213483"},
    "25B21CS072": {"name": "KOTNEY LOHITA", "phone": "9848082509"},
    "25B21CS073": {"name": "ATTI BHADRARAO", "phone": "9573724689"},
    "25B21CS074": {"name": "CHITTURI GOWTHAM", "phone": "9989364292"},
    "25B21CS075": {"name": "NALLAMILLI KALYAN VENKATA REDDY", "phone": "9346697486"},
    "25B21CS076": {"name": "VASA JOHN", "phone": "9703087856"},
    "25B21CS077": {"name": "KARRI SATTI RAJU", "phone": "9666083339"},
    "25B21CS078": {"name": "KALLA ARJUN", "phone": "9885144857"},
    "25B21CS079": {"name": "MUCHCHAKARLA DURGA PRASAD", "phone": "6305399259"},
    "25B21CS080": {"name": "KARRI LOKESH", "phone": "7396528968"},
    "25B21CS081": {"name": "VULAVAKAYALA MANIKANTA SWAMY", "phone": "8688441490"},
    "25B21CS082": {"name": "CHAGANTI PUSHPA LATHA", "phone": "9550325025"},
    "25B21CS083": {"name": "SURAPUREDDY SHYAM CHARAN", "phone": "9989775544"},
    "25B21CS084": {"name": "BEERA LAHARI", "phone": "9963837212"},
    "25B21CS085": {"name": "TOGARA SIVA RAM", "phone": "9010244315"},
    "25B21CS086": {"name": "VANKA LAKSHMI NARAYANA", "phone": "9555992866"},
    "25B21CS087": {"name": "AYODYULA GANGA DURGA PRASAD", "phone": "9493741235"},
    "25B21CS088": {"name": "NALLAMILLI SUMANTH REDDY", "phone": "9849118118"},
    "25B21CS089": {"name": "BOLLU RAMYA SRI", "phone": "8367564985"},
    "25B21CS090": {"name": "KAMISETTI MANIKANTA SAI", "phone": "9963198439"},
    "25B21CS091": {"name": "GANDROTHULA SRI NAGA SATISH", "phone": "9505629908"},
    "25B61CS001": {"name": "LAKSHMI NANITHA PITHANI", "phone": "9581670381"},
    "25B61CS002": {"name": "OMSIRI THOOTA", "phone": "9398826890"}
}

# --- DATABASE FUNCTIONS ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    name TEXT,
                    password TEXT
                )''')
    # Create Usage table to track splits
    c.execute('''CREATE TABLE IF NOT EXISTS usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT,
                    split_date TIMESTAMP
                )''')
    
    # Automatically add missing users to an existing database safely
    for user in INITIAL_USERS:
        c.execute('INSERT OR IGNORE INTO users (name, email, password) VALUES (?, ?, ?)', user)
    
    conn.commit()
    conn.close()

def authenticate(email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT name FROM users WHERE email=? AND password=?', (email, password))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_weekly_usage(email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    c.execute('SELECT COUNT(*) FROM usage WHERE email=? AND split_date >= ?', (email, one_week_ago))
    count = c.fetchone()[0]
    conn.close()
    return count

def log_usage(email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO usage (email, split_date) VALUES (?, ?)', (email, datetime.datetime.now()))
    conn.commit()
    conn.close()

# Initialize the database on app load
init_db()

# --- HELPER FUNCTIONS ---
def extract_text_from_page(page):
    """Extracts text from a PyMuPDF page, falling back to OCR if text is sparse."""
    text = page.get_text("text", sort=True)
    if len(text.strip()) < 15:
        try:
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_text = pytesseract.image_to_string(img)
            text += "\n" + ocr_text
        except Exception as e:
            st.warning(f"OCR failed on a page. Ensure Tesseract is installed. Error: {e}")
    return text

def find_roll_number(text):
    pattern = r'(?i)roll\s*n(?:o|umber)[.\s]*[:\-]?[\s\n]*([A-Za-z0-9]{5,20})'
    match = re.search(pattern, text)
    if match:
        extracted = match.group(1).strip().upper()
        if extracted not in ["BRANCH", "CAMPUS", "STUDENT", "NAME", "DETAILS"]:
            return extracted
    return None

# --- STATE MANAGEMENT ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_name = ""

if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

# --- AUTHENTICATION UI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>Login </h1>", unsafe_allow_html=True)
    st.markdown("""
               <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <img src="https://ik.imagekit.io/syustaging/SYU_PREPROD/LOGO_0H0roO3hk.webp?tr=w-3840" 
                 alt="Aditya University Logo" 
                 style="width: 220px; height: auto;">
        </div>
                """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("User ID", placeholder="e.g., pranavvedula@adityauniversity.in")
        password = st.text_input("Password (your_name@123)", type="password", placeholder="e.g., pranav@123")
        submit_btn = st.form_submit_button("Login")
        
        if submit_btn:
            name = authenticate(email, password)
            if name:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_name = name
                st.success(f"Welcome, {name}!")
                st.rerun()
            else:
                st.error("Invalid Email or Password. Please try again.")
    st.stop() 

# --- SIDEBAR LOGOUT & USAGE STATS ---
splits_used = get_weekly_usage(st.session_state.user_email)
splits_remaining = max(0, WEEKLY_LIMIT - splits_used)

with st.sidebar:
    st.write(f"👤 **{st.session_state.user_name}**")
    st.write(f"✉️ {st.session_state.user_email}")
    st.divider()
    
    st.metric("Weekly Limits Used", f"{splits_used} / {WEEKLY_LIMIT}")
    if splits_remaining == 0:
        st.error("You have reached your limit for this week.")
    else:
        st.success(f"You have {splits_remaining} splits remaining this week.")
        
    st.divider()
    if st.button("Logout", type="primary"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_name = ""
        st.rerun()

# --- MAIN UI (APP LOGIC) ---
st.title("📄 AutoSplit")
st.subheader("Department Of Computer Science Engineering - Aditya University")
st.markdown("""
Upload a bulk PDF containing multiple student records.
*(Max file size: 15MB)*
""")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file is not None:
    if st.session_state.last_uploaded_file != uploaded_file.name:
        st.session_state.last_uploaded_file = uploaded_file.name
        st.session_state.zip_buffer = None
        st.session_state.summary = None

    MAX_SIZE_MB = 15
    file_size_mb = uploaded_file.size / (1024 * 1024)
    
    if file_size_mb > MAX_SIZE_MB:
        st.error(f"File size is {file_size_mb:.2f}MB, which exceeds the 15MB limit. Please upload a smaller file.")
    else:
        st.success(f"File '{uploaded_file.name}' loaded successfully ({file_size_mb:.2f}MB).")
        
        # --- ROLL NUMBER RANGE FILTER UI ---
        st.markdown("### Filter by Roll Number")
        st.write("Specify a range to download papers only for specific students. Leave blank to process all.")
        
        # Check if the logged-in user has a predefined proctoring range
        default_start, default_end = PROCTOR_RANGES.get(st.session_state.user_email, ("", ""))
        
        col1, col2 = st.columns(2)
        with col1:
            start_roll = st.text_input("Start Roll Number", value=default_start, placeholder="e.g., 24B11CS001").strip().upper()
        with col2:
            end_roll = st.text_input("End Roll Number", value=default_end, placeholder="e.g., 24B11CS200").strip().upper()
        
        st.divider()

        if st.session_state.zip_buffer is None:
            if st.button("Split Now ✂️", type="secondary"):
                
                # Check limits before processing
                if splits_remaining <= 0:
                    st.error(f"Limit Reached! You have already used all {WEEKLY_LIMIT} allowed splits for the past 7 days.")
                else:
                  
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    total_pages = 0
                    created_pdfs = 0
                    skipped_pages = []
                    out_of_range_pages = []
                    duplicates_handled = 0
                    
                    roll_number_counts = {}
                    created_rolls_list = [] # List to track successfully extracted rolls for WhatsApp Dashboard
                    individual_pdfs = {} # Store individual PDF bytes for UI download
                    
                    # Process the PDF using Temporary Files
                    with tempfile.TemporaryDirectory() as temp_dir:
                        try:
                            # Load PDF with PyMuPDF
                            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                            total_pages = len(pdf_document)
                            
                            status_text.info("Extracting pages...")
                            
                            for page_num in range(total_pages):
                                page = pdf_document.load_page(page_num)
                                
                                # 1. Extract Text & Roll Number
                                text = extract_text_from_page(page)
                                roll_number = find_roll_number(text)
                                
                                if roll_number:
                                    # 2. Check if the Roll Number is within the specified range
                                    in_range = True
                                    if start_roll and roll_number < start_roll:
                                        in_range = False
                                    if end_roll and roll_number > end_roll:
                                        in_range = False
                                        
                                    if in_range:
                                        # 3. Handle Duplicates
                                        if roll_number in roll_number_counts:
                                            roll_number_counts[roll_number] += 1
                                            duplicates_handled += 1
                                            final_roll_number = f"{roll_number}_{roll_number_counts[roll_number]}"
                                        else:
                                            roll_number_counts[roll_number] = 0
                                            final_roll_number = roll_number
                                        
                                        # 4. Save as individual PDF
                                        output_filename = f"{final_roll_number}.pdf"
                                        output_filepath = os.path.join(temp_dir, output_filename)
                                        
                                        # Create a new PDF with just this page
                                        new_pdf = fitz.open()
                                        new_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
                                        new_pdf.save(output_filepath)
                                        new_pdf.close()
                                        
                                        # Save bytes to memory for individual Quick Download
                                        with open(output_filepath, "rb") as f:
                                            individual_pdfs[final_roll_number] = f.read()
                                        
                                        created_pdfs += 1
                                        created_rolls_list.append(final_roll_number)
                                    else:
                                        out_of_range_pages.append(page_num + 1)
                                else:
                                    skipped_pages.append(page_num + 1)
                                
                                # Update Progress
                                progress = (page_num + 1) / total_pages
                                progress_bar.progress(progress)
                                status_text.text(f"Processed page {page_num + 1} of {total_pages}...")
                            
                            pdf_document.close()
                            
                            # 5. Create ZIP archive in memory
                            status_text.info("Creating ZIP archive...")
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                                for root, _, files in os.walk(temp_dir):
                                    for file in files:
                                        file_path = os.path.join(root, file)
                                        zip_file.write(file_path, arcname=file)
                            
                            # Log usage into DB after successful processing
                            log_usage(st.session_state.user_email)
                            
                            # Store in session state to survive Streamlit widget interactions
                            st.session_state.zip_buffer = zip_buffer.getvalue()
                            st.session_state.summary = {
                                "total": total_pages,
                                "created": created_pdfs,
                                "skipped": skipped_pages,
                                "out_of_range": len(out_of_range_pages),
                                "duplicates": duplicates_handled,
                                "created_rolls": created_rolls_list,
                                "individual_pdfs": individual_pdfs
                            }
                            
                            status_text.success("Processing complete!")
                            st.rerun() 
                            
                        except Exception as e:
                            st.error(f"An error occurred during processing: {e}")

        # --- DISPLAY RESULTS & DOWNLOAD ---
        if st.session_state.summary is not None:
            summary = st.session_state.summary
            
            st.divider()
            st.subheader("Details")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total Pages", summary["total"])
            col2.metric("PDFs Zipped", summary["created"])
            col3.metric("Out of Range", summary["out_of_range"])
            col4.metric("No Roll Found", len(summary["skipped"]))
            col5.metric("Duplicates", summary["duplicates"])
            
            if summary["skipped"]:
                with st.expander("⚠️ View Skipped Pages (No Roll Number Found)"):
                    st.write(f"Pages: {', '.join(map(str, summary['skipped']))}")
            
            if summary["created"] > 0:
                st.divider()
                st.download_button(
                    label="⬇️ Download Selected Papers (ZIP)",
                    data=st.session_state.zip_buffer,
                    file_name="filtered_student_papers.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True
                )
                
                st.divider()
                st.subheader("📲 Parent Communication Dashboard")
                st.info("💡 **Quick Workflow:** Click '⬇️ PDF' to drop the file into your browser's download tray (top right). Then click '💬 Message Parent' and simply **drag the file from the download tray directly into the WhatsApp chat!**")
                
                st.write("#### Student List:")
                
                for roll in summary.get("created_rolls", []):
                    # Handle duplicate numbering like 24B11CS001_1 by splitting
                    base_roll = roll.split('_')[0]
                    student_data = STUDENT_DATA.get(base_roll)
                    
                    if student_data:
                        student_name = student_data["name"]
                        phone_num = student_data["phone"]
                        
                        # Strip all non-digit characters (+, spaces, hyphens) just in case
                        clean_phone = re.sub(r'\D', '', str(phone_num))
                        
                        # Handle formatting based on country code (Assumes India or Zimbabwe from your dataset)
                        if len(clean_phone) == 10:
                            clean_phone = "91" + clean_phone # India numbers
                        elif len(clean_phone) == 9:
                            clean_phone = "263" + clean_phone # Zimbabwe numbers
                        elif len(clean_phone) > 10 and clean_phone.startswith("263"):
                            pass # Already formatted correctly via string stripping
                            
                        # Generate the Pre-filled message and link
                        message = f"Dear Parent, please find attached the recent exam paper for {student_name} (Roll No: {base_roll})."
                        encoded_msg = urllib.parse.quote(message)
                        wa_link = f"https://wa.me/{clean_phone}?text={encoded_msg}"
                        
                        # Display individual download and message button side-by-side
                        col1, col2, col3 = st.columns([2.5, 1, 1.5])
                        with col1:
                            st.markdown(f"**{student_name}**<br><span style='color:gray; font-size:14px;'>📄 {roll}.pdf</span>", unsafe_allow_html=True)
                        with col2:
                            st.download_button(
                                label="⬇️ PDF",
                                data=summary["individual_pdfs"][roll],
                                file_name=f"{roll}.pdf",
                                mime="application/pdf",
                                key=f"dl_{roll}",
                                use_container_width=True
                            )
                        with col3:
                            st.link_button("💬 Message Parent", wa_link, use_container_width=True)
                            
                        st.markdown("<hr style='margin: 5px 0px; border: 0.5px solid #e6e6e6;'>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"📄 **{roll}.pdf** &nbsp;➔&nbsp; ❌ *No phone mapping found in database*")
                        
            else:
                st.warning("No papers matched the given roll number range. Nothing to download.")

# --- FOOTER ---
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        bottom: 10px;
        left: 0;
        width: 100%;
        text-align: center;
        color: gray;
        font-size: 19px;
        padding: 10px;
        background-color: transparent;
    }
    </style>

    <div class="footer">
        Developed by Pranav Vedula | Department of CSE | Aditya University © 2026
    </div>
    """,
    unsafe_allow_html=True
)
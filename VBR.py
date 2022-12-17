#### INFORMASJON #### 
# Filnavn: VBR.py
# Forfatter: Jone Måsøy, André Killingmoe og Eirik Kiland

# Beskrivelse:
# Her lages brukergrensesnittet.

from runpy import run_path
from telnetlib import theNULL
import numpy as np
import customtkinter
import geopy.distance
import numpy
import tkintermapview
from pyproj import Proj, transform
from Brukermain import run



# CTkinter vinduet
VBR = customtkinter.CTk()
VBR.geometry(f"{800}x{600}")
VBR.title("JEA Navigation")


# Initialiserer listene og noen variabler vi bruker i programmet
Startpunktgrafisk = []
Mellompunktgrafisk = []
Sluttpunktgrafisk = []

Startpunkt = []
Mellompunkt = []
Sluttpunkt = []

EastList = []
NorthList = []

Ruteliste = []
Rutegrafisk = []

global Rute
Distanse = float
glider = int



# Venstre vinduramme oppe og nede

frame_left = customtkinter.CTkFrame(master = VBR,width=200)
frame_left.pack(fill="y", side="left")

frame_left_low = customtkinter.CTkFrame(master = frame_left, width = 200)
frame_left_low.pack(side="bottom", fill="x")


# Funksjon for å velge type kart:

def Endre_kart(Nytt_kart):
        if Nytt_kart == "OpenStreetMap":
            Kart.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif Nytt_kart == "Vanlig kart":
            Kart.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif Nytt_kart == "Satelittkart":
            Kart.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

Kartmodus = customtkinter.CTkLabel(frame_left_low, text="Kartmodus:").place(x=1,y=10)

Kartvelger = customtkinter.CTkOptionMenu(frame_left_low, values=["OpenStreetMap", "Vanlig kart", "Satelittkart"],
                                                                       command=Endre_kart).place(x=30,y=40)


# Funksjonen som fjerner markørene. marker.delete() fjerner markørene grafisk, .clear() fjerner innholdet fra listene. 
def fjernstartmarkor():
    for marker in Startpunktgrafisk:
            marker.delete()
    for marker in Mellompunktgrafisk:
            marker.delete()
    Startpunkt.clear()
    Mellompunkt.clear()

def fjernsluttmarkor():
    for marker in Sluttpunktgrafisk:
            marker.delete()
    Sluttpunkt.clear()



# Deklarerer menyoverskrift og knappene som ligger i venstre ramme

Overskrift = customtkinter.CTkLabel(text="Meny", text_font=("Roboto Medium", -16), corner_radius=10).place(x=30,y=10)

Fjernstartmarkør = customtkinter.CTkButton(master=frame_left,
                                            text="Fjern start", width=40,
                                            command=fjernstartmarkor)
Fjernstartmarkør.place(y=50, x=20)


Fjernsluttmarkør = customtkinter.CTkButton(master=frame_left,
                                            text="Fjern slutt", width=40,
                                            command=fjernsluttmarkor)
Fjernsluttmarkør.place(y=50, x=100)


# Funksjonen som fjerner ruten, og resten av knappene tilhørende ruten man fjerner, dersom brukeren velger lag ny rute

def slett_gammel_rute():
    for marker in Sluttpunktgrafisk:
            marker.delete()
    for marker in Startpunktgrafisk:
            marker.delete()
    for marker in Mellompunktgrafisk:
            marker.delete()
    Startpunkt.clear()
    Mellompunkt.clear()
    Sluttpunkt.clear()

    for rute in Rutegrafisk:
        rute.delete()

    Ny_rutelager.place_forget()
    Avstandslabel.place_forget()
    NMlabel.place_forget()
    Tidlabel.place_forget()
    Fart.place_forget()
    Fartsvariabel.place_forget()
    Beregningsknapp.place_forget()
    Slider.place_forget()
    Avstanden.place_forget()
    Tidsvariabel.place_forget()

# Funksjonen som gjør om start- og sluttmarkør til koordinater og legger de i npy. fil. 

def lag_rute():
    StartpunktX, StartpunktY = zip(*Startpunkt)  
    SluttpunktX, SluttpunktY = zip(*Sluttpunkt)


    inProj = Proj(proj='longlat')
    outProj = Proj(proj='utm', zone=33, ellps='WGS84')
    
    # initialiserer listene fyllt med 0er med like mange verdier som det finnes koordinater
    # i ruta
    startx2 = numpy.array(StartpunktX) #startpunktX
    starty2 = numpy.array(StartpunktY) #startpunktY
    sluttx2 = numpy.array(SluttpunktX) #sluttpunktX
    slutty2 = numpy.array(SluttpunktY) #sluttpunktY

    # Transformerer hver koordinat fra grader til xyz
    outstart = transform(inProj,outProj,starty2,startx2)
    outslutt = transform(inProj,outProj,slutty2,sluttx2)

    # Legger de transformerte gradene i en variable
    printstartarray = numpy.column_stack((outstart[1], outstart[0]))
    printsluttarray = numpy.column_stack((outslutt[1], outslutt[0]))

    # Lagrer de transformerte gradene inn i hver sin numpyfil
    numpy.save('printstartarray.npy', printstartarray)
    numpy.save('printsluttarray.npy', printsluttarray)

    # Printer for bekreftelse
    datastart = numpy.load('printstartarray.npy')
    dataslutt = numpy.load('printsluttarray.npy')

    print(datastart)
    print(dataslutt)

    epoch = 0
    while epoch == 0:
        policy, s = run(epoch,printstartarray,printsluttarray)
        action = policy.get(s)
        print("recommended action:")
        print(action)
        epoch += 1


    

# Knapp som igangsetter lag_rute-funksjonen

Rutelager = customtkinter.CTkButton(master=frame_left,
                                            text="Bekreft start/slutt", width=155,
                                            command=lag_rute)
Rutelager.place(y=90, x=20)


# Knapp for å lage ny rute

Ny_rutelager = customtkinter.CTkButton(master=frame_left,
                                        text="Lag ny rute", width=155,
                                        command=slett_gammel_rute)


# Funksjonen som tegner ruten når algoritmen har lagd den ferdig 
def Ruten_tilbake():

    global Distanse
    global Rute
    global NMlabel
    global Tidlabel
    global Fart
    global Beregningsknapp
    global Avstandslabel
    global Avstanden
    global OverfDistanse
    Ruteliste = numpy.load('Ruta.npy')
    Kartrute = Ruteliste

# Finner distansen til ruta basert på avstanden mellom hvert punkt er. 

    Distanse = 0
    for i in range(len(Kartrute)):
        if i == len(Kartrute) - 1: 
            break
        koordinat1 = Kartrute[i]
        koordinat2 = Kartrute[i+1]
        EnkelDistanse = geopy.distance.geodesic(koordinat1, koordinat2).km 
        Distanse = Distanse + EnkelDistanse

    # Begrenser distansen til to desimaler
    Distanse = format(Distanse, ".2f")   
    
    # Denne legger ruten i en liste og tegner den
    Rutegrafisk.append(Kart.set_path(position_list=(Kartrute)))
    
#Linjene under navngir og plasserer alle knapper og labels som skal frem etter funksjonen har kjørt

    Ruteoptimaliserer = customtkinter.CTkLabel(text="Ruteoptimaliserer", text_font=("Roboto Medium", -11), corner_radius=10).place(x=25,y=190)


    Slider.place(x=10,y=220)
    Slider.set(0)

    Avstanden = customtkinter.CTkLabel(master=frame_left,
                                                   text="Avstand:",
                                                   height=20, width=80,
                                                   corner_radius=6,fg_color=("white", "gray38"))
    Avstanden.place(x=10, y=250)

    Avstandslabel = customtkinter.CTkLabel(master=frame_left, text=Distanse, 
                                                   height=20, width=40,
                                                   corner_radius=6)
    Avstandslabel.place(x=100, y=250)

    NMlabel = customtkinter.CTkLabel(master=frame_left, text="NM", 
                                                   height=20, width=20,
                                                   corner_radius=6)
    NMlabel.place(x=140, y=250)  

                                
    Tidlabel = customtkinter.CTkLabel(master=frame_left,
                                                   text="Tid:",
                                                   height=20, width=80,
                                                   corner_radius=6, fg_color=("white", "gray38"))
    Tidlabel.place(x=10, y=280)


    Fart = customtkinter.CTkLabel(master=frame_left, text="Fart:",
                                                height=20, width=80,
                                                corner_radius=6,  fg_color=("white", "gray38"))
    Fart.place(x=10, y=310)

    Ny_rutelager.place(y=130, x=20)
    Fartsvariabel.place(x=100, y=310)

    Beregningsknapp = customtkinter.CTkButton(text="Kalkuler tid", command=Kalkuler_tid)
    Beregningsknapp.place(x=30,y=340)

   
Fartsvariabel = customtkinter.CTkEntry(master=frame_left,
                                        height=20, width=80,corner_radius=6)


#Funksjonen som gjør at glidebryteren fungerer. Denne avgjør hvor mange punkter som skal være med i ruten.

def Endreglider(glider):

    # Det første denne gjør er å fjerne den gamle ruten. Dette skjer hver gang brukeren rører på glidebryteren
    global OverfDistanse
    Rutegrafisk.clear
    for Rute in Rutegrafisk:
            Rute.delete()
    
    # Glider = 0 vil ta med alle punktene i ruten. Denne vil bli veldig svingete og dermed urealistisk lang
    if glider == 0:
        Ruteliste = numpy.load('Ruta.npy')
        kartrute = Ruteliste


        Distanse = 0
        for i in range(len(kartrute)):
            if i == len(kartrute) - 1: 
                break
            koordinat1 = kartrute[i]
            koordinat2 = kartrute[i+1]
            EnkelDistanse = geopy.distance.geodesic(koordinat1, koordinat2).km 
            Distanse = Distanse + EnkelDistanse

        Distanse = format(Distanse, ".2f")   
        # Lager ruten på nytt med nytt antall punkter.
        Rutegrafisk.append(Kart.set_path(position_list=(kartrute)))

        Avstandslabel.configure(text=Distanse)
        OverfDistanse = Distanse

    # Glider = 1 vil kun beholde hvert 4. punkt
    elif glider == 1:
        # Starter med å laste inn ruten fra numpyfilen
        Ruteliste = numpy.load('Ruta.npy')
        # [0::4] sier at den skal starte på 0. punkt (Dette er 1. punkt) og dermed hente ut hver 4. verdi fra listen.
        kartrute = Ruteliste[0::6] 
        # Setter den nye lengden til Ruteliste inn i variabelen kartrute_lengde
        kartrute_lengde = len(Ruteliste)
        # Henter ut det siste punktet i ruten og legger den i variabelen DestinasjonsKartrute
        DestinasjonKartrute = Ruteliste[kartrute_lengde - 1]
        # Legger nye ruten inn i kartrute sammen med siste punktet i ruten. Denne er viktig å legge til ettersom man hopper over så mange punkter i ruten.
        # Har man den ikke med kan sluttdestinasjonen bli helt feil sted.
        kartrute = numpy.append(kartrute, [DestinasjonKartrute], axis=0)



        Distanse = 0
        for i in range(len(kartrute)):
            if i == len(kartrute) - 1: 
                break
            koordinat1 = kartrute[i]
            koordinat2 = kartrute[i+1]
            EnkelDistanse = geopy.distance.geodesic(koordinat1, koordinat2).km 
            Distanse = Distanse + EnkelDistanse

        Distanse = format(Distanse, ".2f")   

        Rutegrafisk.append(Kart.set_path(position_list=(kartrute)))

        Avstandslabel.configure(text=Distanse)

        OverfDistanse = Distanse

    # Glider = 2 vil kun beholde hvert 8. punkt
    elif glider == 2:
        Ruteliste = numpy.load('Ruta.npy')
        kartrute = Ruteliste[0::12]
        kartrute_lengde = len(Ruteliste)
        DestinasjonKartrute = Ruteliste[kartrute_lengde - 1]
        kartrute = numpy.append(kartrute, [DestinasjonKartrute], axis=0)

        Distanse = 0
        for i in range(len(kartrute)):
            if i == len(kartrute) - 1: 
                break
            koordinat1 = kartrute[i]
            koordinat2 = kartrute[i+1]
            EnkelDistanse = geopy.distance.geodesic(koordinat1, koordinat2).km 
            Distanse = Distanse + EnkelDistanse

        Distanse = format(Distanse, ".2f")   

        Rutegrafisk.append(Kart.set_path(position_list=(kartrute)))

        Avstandslabel.configure(text=Distanse)
        OverfDistanse = Distanse

    # Glider = 3 vil kun beholde hvert 12. punkt
    elif glider == 3:
        Ruteliste = numpy.load('Ruta.npy')
        kartrute = Ruteliste[0::18]
        kartrute_lengde = len(Ruteliste)
        DestinasjonKartrute = Ruteliste[kartrute_lengde - 1]
        kartrute = numpy.append(kartrute, [DestinasjonKartrute], axis=0)


        Distanse = 0
        for i in range(len(kartrute)):
            if i == len(kartrute) - 1: 
                break
            koordinat1 = kartrute[i]
            koordinat2 = kartrute[i+1]
            EnkelDistanse = geopy.distance.geodesic(koordinat1, koordinat2).km 
            Distanse = Distanse + EnkelDistanse

        Distanse = format(Distanse, ".2f")   

        Rutegrafisk.append(Kart.set_path(position_list=(kartrute)))

        Avstandslabel.configure(text=Distanse)
        OverfDistanse = Distanse

    # Glider = 4 vil kun beholde hvert 16. punkt
    elif glider == 4:
        Ruteliste = numpy.load('Ruta.npy')
        kartrute = Ruteliste[0::24]
        kartrute_lengde = len(Ruteliste)
        DestinasjonKartrute = Ruteliste[kartrute_lengde - 1]
        kartrute = numpy.append(kartrute, [DestinasjonKartrute], axis=0)


        Distanse = 0
        for i in range(len(kartrute)):
            if i == len(kartrute) - 1: 
                break
            koordinat1 = kartrute[i]
            koordinat2 = kartrute[i+1]
            EnkelDistanse = geopy.distance.geodesic(koordinat1, koordinat2).km 
            Distanse = Distanse + EnkelDistanse

        Distanse = format(Distanse, ".2f")   

        Rutegrafisk.append(Kart.set_path(position_list=(kartrute)))

        Avstandslabel.configure(text=Distanse)
        OverfDistanse = Distanse

    # Glider = 5 vil kun beholde hvert 20. punkt
    elif glider == 5:
        Ruteliste = numpy.load('Ruta.npy')
        kartrute = Ruteliste[0::30]
        kartrute_lengde = len(Ruteliste)
        DestinasjonKartrute = Ruteliste[kartrute_lengde - 1]
        kartrute = numpy.append(kartrute, [DestinasjonKartrute], axis=0)


        Distanse = 0
        for i in range(len(kartrute)):
            if i == len(kartrute) - 1: 
                break
            koordinat1 = kartrute[i]
            koordinat2 = kartrute[i+1]
            EnkelDistanse = geopy.distance.geodesic(koordinat1, koordinat2).km 
            Distanse = Distanse + EnkelDistanse

        Distanse = format(Distanse, ".2f")   

        Rutegrafisk.append(Kart.set_path(position_list=(kartrute)))

        Avstandslabel.configure(text=Distanse)
        OverfDistanse = Distanse


# definerer slideren og legger sliderverdien inn i variabelen glider nedenfor
Slider = customtkinter.CTkSlider(master=frame_left,
                                    command=Endreglider,
                                    from_=0, to=5, number_of_steps=5,
                                    width=170)
glider = Slider.get()


# Funksjonen som kalkulerer tiden det vil ta å seile ruten. Fart er input fra brukeren.
def Kalkuler_tid():

    if OverfDistanse != 0:
        Distanse = OverfDistanse

    knop = Fartsvariabel.get()
    Fart = float(knop)
    Avstand = float(Distanse)

    Tid = Avstand / Fart
    Antallminutter = Tid * 60
    Antallsekunder = ((Antallminutter % 1)*100) * 60/100
    AM = int(Antallminutter)
    AS = int(Antallsekunder)
    Totaltid = (AM, "Min,", AS, "Sek")
    global Tidsvariabel
    Tidsvariabel = customtkinter.CTkLabel(master=frame_left, text=Totaltid, 
                                                   height=20, width=80,
                                                   corner_radius=6)
    Tidsvariabel.place(x=100, y=280) 


# Toppramme
frame_top = customtkinter.CTkFrame(master = VBR)
frame_top.pack(fill="x", side="top")


# Søkefunksjonen som tilhører søkebaren. Funksjonen som setter kartet over stedet man søker på.
def Søkefunksjon(event=None):
    Kart.set_address(Søkefelt.get())


Søkefelt = customtkinter.CTkEntry(master=frame_top,
                                    placeholder_text="Adresse..",
                                    width=450)
Søkefelt.pack(padx=5, pady=10, side="left")

Søkefelt.entry.bind("<Return>", Søkefunksjon)

Søkeknapp = customtkinter.CTkButton(master=frame_top,
                                    text="Søk",
                                    width=90,
                                    command=Søkefunksjon)
Søkeknapp.pack(side="left", padx=15)



# Høyre ramme
frame_right = customtkinter.CTkFrame(master=VBR)
frame_right.pack(fill="both", expand=True, side="right")

# Kartet
Kart = tkintermapview.TkinterMapView(master=frame_right)
Kart.pack(fill='both', expand=True)

# Sjøkartet (overlay)
Kart.set_overlay_tile_server("http://tiles.openseamap.org/seamark//{z}/{x}/{y}.png")

# Setter startposisjon
Kart.set_position(60.3888429, 5.3242385)  # Bergen
Kart.set_zoom(10)






# Høyreklikk funksjonen som setter startmarkør. Den vil først slette eventuelle markører som er satt fra før, slik at det kun er én startmarkør. 
# Dette skjer både grafisk og i listen markørene ligger i. Så printer den ut koordinatene og legger markøren i en liste.
def add_startmarker_event(coords):
    for marker in Startpunktgrafisk:
        marker.delete()
        Startpunktgrafisk.clear()
        Startpunkt.clear()
    print("Markør - start:", coords)
    Startpunktgrafisk.append(Kart.set_marker(coords[0], coords[1], text="Start"))
    Startpunkt.append(coords)

Kart.add_right_click_menu_command(label="Startposisjon",
                                        command=add_startmarker_event,
                                        pass_coords=True)


# Høyreklikk funksjonen som setter mellommarkør
def add_mellommarker_event(coords):
        print("Markør - Mellomstopp:", coords)
        Mellompunktgrafisk.append(Kart.set_marker(coords[0], coords[1], text="Mellomstopp"))
        Mellompunkt.append(coords)


Kart.add_right_click_menu_command(label="Mellomstopp",
                                        command=add_mellommarker_event,
                                        pass_coords=True)

# Høyreklikk funksjonen som setter sluttmarkør
def add_sluttmarker_event(coords):
        for marker in Sluttpunktgrafisk:
            marker.delete()
            Sluttpunktgrafisk.clear()
            Sluttpunkt.clear()
        print("Markør - destinasjon:", coords)
        Sluttpunktgrafisk.append(Kart.set_marker(coords[0], coords[1], text="Destinasjon"))
        Sluttpunkt.append(coords)

Kart.add_right_click_menu_command(label="Sluttposisjon",
                                        command=add_sluttmarker_event,
                                        pass_coords=True)


# Høyreklikk funksjonen som aktiverer "Ruten_tilbake". Denne må brukes når algoritmen har lagd ruten

Kart.add_right_click_menu_command(label="Tegn rute",
                                 command=Ruten_tilbake)


VBR.mainloop()
"""
Requisitos del trabajo práctico de Gestion de VideoClub:
- Tendrán las siguientes tablas:
    1) clientes : con los siguientes campos en cada registro: DNI como primary key, Nombre Completo, Telefono, direccion, estado como foreign key.
    2) peliculas (para el videoclub): campos: código de barra como primary key, titulo, genero, estado como foreign key.
    3) prestamos: campos: ID como primary key, DNI, código de barras, estado, fecha prestamo como date y fecha devolucion como date.

Deberán mostrar un menú con las siguientes opciones:
   0 - Consulta de disponibilidad de la pelicula: debe indicar "Disponible" si el estado es D, o "En préstamo al cliente {nombreCompleto}" si el estado es P)
   1 - Préstamo de película : puede tener un sub-Menú que tenga las opciones:
        A - Consultar todos las películas disponibles (devuelve todos los campos de las películas con estado vacío "")
        B - Registrar préstamo (busca la película y cambia estado de la película y el cliente a P)
        C - Registrar Devolución (pide el codigo de barras de la pelicula y cambia el estado de la pelicula y el cliente a vacio "", además de agregar la fecha de devolución en la tabla prestamos)
    2 - Gestión del cliente: tendrá un sub-menú:
        A - Alta de cliente
        C - Consulta estado del cliente
        M - Modificar teléfono o direccion del cliente
        E - Eliminar cliente (no se elimina el registro, sino se cambia el campo estado por ejemplo "B" de baja)
    3 - Gestión de película: tendrá un sub-menu:
        A - Alta de película
        C - Consultar un película (pide el nombre de la pelicula y muestra todos los campos)
        M - Modificar película
        E - Eliminar película
"""
#!/usr/bin/env python
#-*- coding: utf-8 -*-
import mariadb
import os

mydb = ""
mycursor = ""

def conectarAdmin():
    try:
        mydb = mariadb.connect(
            host="127.0.0.1",
            user="root",
            autocommit=True
        )
        return mydb
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None

def crearBase(mydb):
    try:
        mycursor = mydb.cursor()
        mycursor.execute("CREATE DATABASE IF NOT EXISTS VIDEOCLUBGRUPO7")
        mycursor.execute("USE VIDEOCLUBGRUPO7")
        print("Base de datos VIDEOCLUBGRUPO7 creada correctamente.")
    except mariadb.ProgrammingError:
        print("La base VIDEOCLUBGRUPO7 ya existe")

def conectarBase():
    while True:
        try:
            mydb = mariadb.connect(
                host="127.0.0.1",
                user="root",
                database="VIDEOCLUBGRUPO7"
            )
            mycursor = mydb.cursor()
            return mycursor, mydb
        except mariadb.Error as e:
            if "Unknown database" in str(e):
                # Crea la base si no existe
                crearBase(conectarAdmin())
                print("Intentando reconectar...")
            else:
                print(f"Error: {e}")
                print("Intentando reconectar...")


def crearTabla(mycursor):
    try:
        mycursor.execute("CREATE TABLE IF NOT EXISTS clientes (dni INT PRIMARY KEY, nombreCompleto VARCHAR(255), direccion VARCHAR(255), telefono INT, estado CHAR(1))")
        print("Tabla clientes creada correctamente.")
    except mariadb.OperationalError:
        print("La tabla clientes ya existe")

def insertoRegis(mycursor, mydb):
    val = [
        (42123123, 'Pedro Gomez', 'Santa Rosa 4', 45673456, 'P'),
        (11111111, 'Amalia Perez', 'Dillon 652', 47567676, ""),
        (22222222, 'Analia Gonzalez', 'Aguado 21', 45657676, 'P'),
        (33333333, 'Miguel Lopez', 'Muñiz 345', 48569898, 'B')
    ]
    sql = "INSERT INTO clientes (dni, nombreCompleto, direccion, telefono, estado) VALUES (%s, %s, %s, %s, %s)"
    mycursor.executemany(sql, val)
    mydb.commit()
    print(mycursor.rowcount, "Fueron insertados.")
    mydb.close()  # Cierra la conexión

def limpioPantalla():
    sisOper = os.name
    if sisOper == "posix":   # si fuera UNIX, mac para Apple, java para maquina virtual Java
        os.system("clear")
    elif sisOper == "ce" or sisOper == "nt" or sisOper == "dos":  # windows
        os.system("cls")

def crearTablaPrestamos(mycursor):
    try:
        mycursor.execute("CREATE TABLE IF NOT EXISTS prestamos (ID INT AUTO_INCREMENT PRIMARY KEY, DNI INT, codigoBarras BIGINT, estado CHAR(1), fechaPrestamo DATE, fechaDevolucion DATE, FOREIGN KEY (codigoBarras) REFERENCES peliculas(codigoBarras), FOREIGN KEY (DNI) REFERENCES clientes(DNI))")
        print("Tabla prestamos creada correctamente.")
    except mariadb.OperationalError:
        print("La tabla prestamos ya existe")


def crearTablaPeliculas(mycursor):
    try:
        mycursor.execute("CREATE TABLE IF NOT EXISTS peliculas (codigoBarras BIGINT PRIMARY KEY, titulo VARCHAR(255), genero VARCHAR(255), estado CHAR(1))")
        print("Tabla peliculas creada correctamente.")
    except mariadb.OperationalError:
        print("La tabla peliculas ya existe")

def altaPelicula(mycursor, mydb):
    while True:
        try:
            mycursor.execute("USE VIDEOCLUBGRUPO7")
            codigo_barras = int(input("Ingrese un código de barras de 13 dígitos para la película: "))
        except ValueError:
            print("El código de barras debe ser un número entero.")
        else:
            if len(str(codigo_barras)) == 13:
                break  # Sale del bucle si el código de barras es válido
            else:
                print("El código de barras debe tener exactamente 13 dígitos.")

    try:
        titulo = input("Ingrese el título de la película: ")
        genero = input("Ingrese el género de la película: ")
        estado = ' '
        sql = "INSERT INTO peliculas (codigoBarras, titulo, genero, estado) VALUES (%s, %s, %s, %s)"
        val = (codigo_barras, titulo, genero, estado)
        mycursor.execute(sql, val)
        mydb.commit()
        print("Película registrada exitosamente.")
    except mariadb.Error as e:
        print(f"Error al ejecutar la consulta: {e}")
    finally:
        if mydb:
            mydb.close()


def modificarPelicula(mycursor, mydb):
    try:
        mycursor.execute("USE VIDEOCLUBGRUPO7")
        codigo_barras = int(input("Ingrese el código de barras de la película a modificar: "))

        # Verificar si la película está prestada antes de solicitar el nuevo título y género
        mycursor.execute("SELECT estado FROM peliculas WHERE codigoBarras = %s", (codigo_barras,))
        estado_actual = mycursor.fetchone()

        if estado_actual and estado_actual[0] == 'P':
            print("No se puede modificar el título o el género de una película prestada.")
        else:
            nuevo_titulo = input("Ingrese el nuevo título de la película: ")
            nuevo_genero = input("Ingrese el nuevo género de la película: ")

            sql = "UPDATE peliculas SET titulo = %s, genero = %s WHERE codigoBarras = %s"
            val = (nuevo_titulo, nuevo_genero, codigo_barras)
            mycursor.execute(sql, val)
            mydb.commit()
            print("Películula modificada exitosamente.")
    except mariadb.Error as e:
        print(f"Error al ejecutar la consulta: {e}")
    finally:
        if mydb:
            mydb.close()

def eliminarPelicula(mycursor, mydb):
    try:
        mycursor.execute("USE VIDEOCLUBGRUPO7")
        codigo_barras = int(input("Ingrese el código de barras de la película a eliminar: "))
        
        # Verificar si la película está prestada antes de dar de baja
        mycursor.execute("SELECT estado FROM peliculas WHERE codigoBarras = %s", (codigo_barras,))
        estado_actual = mycursor.fetchone()

        if estado_actual and estado_actual[0] == 'P':
            print("La película está en préstamo actualmente. Por lo tanto, no se puede dar de baja.")
        else:
            sql = "UPDATE peliculas SET estado = 'B' WHERE codigoBarras = %s"
            val = (codigo_barras,)
            mycursor.execute(sql, val)
            mydb.commit()
            print("La película fue dada de baja exitosamente.")
    except mariadb.Error as e:
        print(f"Error al ejecutar la consulta: {e}")
    finally:
        if mydb:
            mydb.close()


def consultaClientes(mycursor):
    dni = int(input("Ingrese DNI de la persona: "))
    mycursor.execute("SELECT nombreCompleto, estado FROM clientes WHERE dni = " + str(dni))
    myresultado = mycursor.fetchall()
    if len(myresultado) == 0:
        print("El DNI", dni, "no pertenece a un cliente del videoclub.")
    else:
        print("El estado del cliente", myresultado[0][0], "es:", myresultado[0][1])

def validoDNI(mycursor, mydb):
    while True:
        try:
            dni = int(input("Ingrese DNI de la persona: "))

            # Verificar que el dni tenga 7 u 8 dígitos.
            dni_str = str(dni)
            if len(dni_str) not in (7, 8):
                print("Error: El DNI debe tener 7 u 8 dígitos.")
                continue

            # Verificar que si el cliente ya figura en la base.
            mycursor.execute("SELECT * FROM clientes WHERE dni = %s", (dni,))
            existing_client = mycursor.fetchone()

            if existing_client:
                existing_estado = existing_client[4]

                if existing_estado == 'B':
                    # Si el cliente está dado de baja, cambiar el estado a vacío.
                    mycursor.execute("UPDATE clientes SET estado = '' WHERE dni = %s", (dni,))
                    mydb.commit()
                    print("El cliente dado de baja fue dado de alta nuevamente.")
                elif existing_estado == 'P':
                    print("El cliente ya existe y tiene una película en préstamo.")
                else:
                    print("Cliente ya registrado, ingrese un DNI diferente.")
            else:
                break  # Salir del bucle si el cliente no existe

        except ValueError:
            print("Error: Ingrese un número de DNI válido.")

    return dni



def nuevoCliente(mycursor, mydb):
    try:
        # Crear la tabla si no existe
        crearTablaClientes(mycursor)

        while True:
            dni = validoDNI(mycursor, mydb)
            nombreCompleto = input("Ingrese el Nombre y Apellido: ")
            direccion = input("Ingrese la dirección: ")
            telefono = int(input("Ingrese el teléfono: "))

            # Establecer un estado vacío para los clientes nuevos.
            estado = ''

            # Insertar nuevo cliente
            sql = "INSERT INTO clientes (dni, nombreCompleto, direccion, telefono, estado) VALUES (%s, %s, %s, %s, %s)"
            val = (dni, nombreCompleto, direccion, telefono, estado)
            mycursor.execute(sql, val)
            mydb.commit()

            print(mycursor.rowcount, "Los datos del cliente se guardaron exitosamente.")
            break  # Salir del bucle
    except Exception as e:
        print("Error:", e)


    except mariadb.IntegrityError:
        print("DNI existente")
    except ValueError:
        print("Error: Ingrese un número de teléfono válido.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if mydb:
            mydb.close()




def modif_Telefono(mycursor, mydb):
    try:
        mycursor.execute("USE VIDEOCLUBGRUPO7")
        dni = int(input("Ingrese el DNI del cliente a modificar: "))
        
        # Validar que el teléfono tenga diez dígitos
        telefono = input("Ingrese el nuevo teléfono (10 dígitos): ")
        if not telefono.isdigit() or len(telefono) != 10:
            print("El número de teléfono ingresado no es válido.")
            return

        telefono = int(telefono)

        sql = "UPDATE clientes SET telefono = %s WHERE dni = %s"
        val = (telefono, dni)

        mycursor.execute(sql, val)
        mydb.commit()

        if mycursor.rowcount > 0:
            print("Registro modificado exitosamente.")
        else:
            print("No se encontró ningún registro para el DNI proporcionado.")
    except mariadb.Error as e:
        print(f"Error al ejecutar la consulta: {e}")
    finally:
        if mydb:
            mydb.close()

def baja_Cliente(mycursor, mydb):
    try:
        mycursor.execute("USE VIDEOCLUBGRUPO7")  # Verificar que se seleccione la base correcta
        dni = int(input("Ingrese DNI del cliente a dar de baja:"))

        # Verificar que el cliente exista
        mycursor.execute("SELECT dni, estado FROM clientes WHERE dni = %s", (dni,))
        cliente_info = mycursor.fetchone()

        if cliente_info:
            if cliente_info[1] == 'P':
                print("Este cliente tiene una película prestada, no se puede dar de baja hasta que la devuelva.")
            else:
                # Actualizar el estado a 'B' de baja
                sql = "UPDATE clientes SET estado = 'B' WHERE dni = %s"
                val = (dni,)
                mycursor.execute(sql, val)
                mydb.commit()
                print(mycursor.rowcount, "Registro modificado (cliente dado de baja).")
        else:
            print("Cliente no registrado.")
    except ValueError:
        print("Error: Ingrese un número de DNI válido.")
    except mariadb.Error as e:
        print(f"Error al ejecutar la consulta: {e}")
    finally:
        if mydb:
            mydb.close()


def listado_Clientes(mycursor):
    # mostrar listado de todos los clientes en la tabla
    mycursor.execute("SELECT * FROM cliente")
    myresultado = mycursor.fetchall()
    if len(myresultado) == 0:
        print("No se han encontrado registros.")
    else:
        print("|---------------------------------------------------------------------|")
        print("|   DNI   ", "| Nombre y Apellido", "|  Dirección  ", "| Teléfono ", "|Estado|")
        print("|---------------------------------------------------------------------|")
        for ind in myresultado:
            print("|", ind[0], "|", ind[1], "|", ind[2], "|", ind[3], "|", ind[4],"|")
            print("|-----------------------------------------------------------------|")
        mydb.close()  

def crearTablaClientes(mycursor):
    try:
        mycursor.execute("CREATE TABLE IF NOT EXISTS clientes (DNI INT PRIMARY KEY, nombreCompleto VARCHAR(255), direccion VARCHAR(255), telefono BIGINT, estado CHAR(1))")
        print("Tabla clientes creada correctamente.")
    except mariadb.OperationalError:
        print("La tabla clientes ya existe")


def consultar_disponibilidad_pelicula(mycursor):
    try:
        # Verifica que exista la tabla peliculas
        mycursor.execute("SHOW TABLES LIKE 'peliculas'")
        peliculas_table_exists = mycursor.fetchone()

        if not peliculas_table_exists:
            # Crea la tabla películas si no existe
            crearTablaPeliculas(mycursor)
            print("Creando la tabla 'peliculas'...")

        mycursor.execute("SELECT COUNT(*) FROM peliculas WHERE estado = ''")
        peliculas_count = mycursor.fetchone()[0]

        if peliculas_count == 0:
            print("No hay más películas disponibles en este momento.")
        else:
            mycursor.execute("SELECT * FROM peliculas WHERE estado = ''")
            registros = mycursor.fetchall()

            print("|----------------------------------------------------------------------|")
            print("| Código Barras    | ", "   Título    |", "    Género   |", "  Estado  |")
            print("|----------------------------------------------------------------------|")
            for registro in registros:
                print(f"| {registro[0]} |   {registro[1]}    | {registro[2]} |   {registro[3]} |")
                print("|----------------------------------------------------------------------|")
    except mariadb.Error as e:
        print(f"Error al ejecutar la consulta: {e}")




def registrar_prestamo_pelicula(mycursor, mydb):
    try:
        dni = int(input("Ingrese el DNI del cliente: "))

        # Verifica si el cliente existe
        mycursor.execute("SELECT * FROM clientes WHERE DNI = %s", (dni,))
        client = mycursor.fetchone()

        if not client:
            print("Este cliente no está registrado.")
            return

        # Check if the client is not given of low ('B' or 'E')
        if client[4] in ('B', 'E'):
            print("El cliente fue dado de baja, no puede recibir préstamos. Intente dar de alta el cliente nuevamente.")
            return

        # Cliente existe, procede con el préstamo
        codigo_barras = int(input("Ingrese el código de barras de la película: "))

        # Verifica si la película existe
        mycursor.execute("SELECT * FROM peliculas WHERE codigoBarras = %s", (codigo_barras,))
        movie = mycursor.fetchone()

        if not movie:
            print("Esta película no está registrada.")
            return

        # Verifica si la tabla 'prestamos' existe, si no, la crea
        mycursor.execute("SHOW TABLES LIKE 'prestamos'")
        prestamos_table_exists = mycursor.fetchone()

        if not prestamos_table_exists:
            crearTablaPrestamos(mycursor)
            print("Creando la tabla 'prestamos'...")

        # Película existe, procede con el préstamo
        sql_insert_loan = "INSERT INTO prestamos (DNI, codigoBarras, estado, fechaPrestamo) VALUES (%s, %s, 'P', CURRENT_DATE)"
        val_insert_loan = (dni, codigo_barras)

        mycursor.execute(sql_insert_loan, val_insert_loan)
        mydb.commit()

        # Actualiza los estados del cliente y la película a 'P' (prestamo)
        mycursor.execute("UPDATE clientes SET estado = 'P' WHERE DNI = %s", (dni,))
        mycursor.execute("UPDATE peliculas SET estado = 'P' WHERE codigoBarras = %s", (codigo_barras,))
        mydb.commit()

        # Muestra el mensaje de confirmación
        print(f"El cliente {client[1]} ha retirado la película {movie[1]}.")

    except ValueError:
        print("Error: Ingrese números válidos para DNI y código de barras.")
    except mariadb.Error as e:
        print(f"Error al ejecutar la consulta: {e}")


def registrar_devolucion_pelicula(mycursor, mydb):
    try:
        codigo_barras = int(input("Ingrese el código de barras de la película que se devolverá: "))

        # Verificar si la película está prestada
        mycursor.execute("SELECT * FROM prestamos WHERE codigoBarras = %s AND estado = 'P'", (codigo_barras,))
        peliculaPrestada = mycursor.fetchone()

        if peliculaPrestada:
            dni = peliculaPrestada[1]

            mycursor.execute("UPDATE prestamos SET estado = 'D', fechaDevolucion = CURRENT_DATE WHERE codigoBarras = %s AND estado = 'P'", (codigo_barras,))
            mycursor.execute("UPDATE clientes SET estado = '' WHERE DNI = %s", (dni,))
            mycursor.execute("UPDATE peliculas SET estado = '' WHERE codigoBarras = %s", (codigo_barras,))
            mydb.commit()
            print("Devolución registrada exitosamente.")
        else:
            print("La película no está actualmente en préstamo.")
    except ValueError:
        print("Error: Ingrese un número válido como código de barras.")
    except mariadb.Error as e:
        print(f"Error al ejecutar la consulta: {e}")


# ---------------------------------- parte principal -----------------------------------
mydb = conectarAdmin()

if mydb:
    mycursor = mydb.cursor()


    while True:
        print("MENU:")
        print("0 - Consulta disponibilidad de película")
        print("1 - Préstamo de Película")
        print("2 - Gestión del cliente")
        print("3 - Gestión de Películas")
        print("7 - Salir")
        opcion = input("Ingrese la opción deseada: ")

        if opcion == '0':
            limpioPantalla()
            mycursor, mydb = conectarBase()
            crearTablaPrestamos(mycursor)
            consultar_disponibilidad_pelicula(mycursor)


        elif opcion == '1':
            limpioPantalla()
            mycursor, mydb = conectarBase()
            crearTablaPrestamos(mycursor)
            print("SUB-MENU PRÉSTAMO DE PELÍCULA:")
            print("A - Consultar películas disponibles")
            print("B - Registrar préstamo")
            print("C - Registrar Devolución")

            opcion_submenu = input("Ingrese la opción deseada: ")

            if opcion_submenu.upper() == 'A':
                limpioPantalla()
                consultar_disponibilidad_pelicula(mycursor)
            elif opcion_submenu.upper() == 'B':
                limpioPantalla()
                registrar_prestamo_pelicula(mycursor, mydb)
            elif opcion_submenu.upper() == 'C':
                limpioPantalla()
                registrar_devolucion_pelicula(mycursor, mydb)
            else:
                print("Opción no válida. Intente nuevamente.")

        elif opcion == '2':
            limpioPantalla()
            mycursor, mydb = conectarBase()
            print("SUB-MENU GESTIÓN DEL CLIENTE:")
            print("A - Alta de cliente")
            print("C - Consulta estado del cliente")
            print("M - Modificar teléfono o dirección")
            print("E - Dar de baja el cliente")

            opcion_submenu = input("Ingrese la opción deseada: ")

            if opcion_submenu.upper() == 'A':
                limpioPantalla()
                nuevoCliente(mycursor, mydb)
            elif opcion_submenu.upper() == 'C':
                limpioPantalla()
                consultaClientes(mycursor)
            elif opcion_submenu.upper() == 'M':
                limpioPantalla()
                modif_Telefono(mycursor, mydb)
            elif opcion_submenu.upper() == 'E':
                limpioPantalla()
                baja_Cliente(mycursor, mydb)
            else:
                print("Opción no válida. Intente nuevamente.")

        elif opcion == '3':
            limpioPantalla()
            mycursor, mydb = conectarBase()
            crearTablaPeliculas(mycursor)#Para asegurarme de que la tabla exista antes de intentar modificarla.
            print("SUB-MENU GESTIÓN DE PELÍCULAS:")
            print("A - Alta de Película")
            print("C - Consultar una película")
            print("M - Modificar Película")
            print("E - Eliminar Película")

            opcion_submenu = input("Ingrese la opción deseada: ")

            if opcion_submenu.upper() == 'A':
                limpioPantalla()
                altaPelicula(mycursor, mydb)
            elif opcion_submenu.upper() == 'C':
                limpioPantalla()
                consultar_disponibilidad_pelicula(mycursor)
            elif opcion_submenu.upper() == 'M':
                limpioPantalla()
                modificarPelicula(mycursor, mydb)
            elif opcion_submenu.upper() == 'E':
                limpioPantalla()
                eliminarPelicula(mycursor, mydb)
            else:
                print("Opción no válida. Intente nuevamente.")

        elif opcion == '7':
            limpioPantalla()
            print("Gracias por utilizar el Administrador de Videoclubes del Grupo 7.")
            break

        else:
            print("Opción no válida. Intente nuevamente.")

else:
    print("Error: No se pudo conectar a la base de datos.")

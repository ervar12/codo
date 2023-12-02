#--------------------------------------------------------------------

from flask import Flask, request, jsonify
from flask import request


from flask_cors import CORS


import mysql.connector


from werkzeug.utils import secure_filename


import os
import time
#--------------------------------------------------------------------



app2= Flask(__name__)
CORS(app2)  

#--------------------------------------------------------------------
class Catalogo:
    #----------------------------------------------------------------
    # Constructor de la clase
    def __init__(self, host, user, password, database):
        
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        self.cursor = self.conn.cursor(dictionary=True)
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
            id_prod INT AUTO_INCREMENT PRIMARY KEY,
            nombre_prod VARCHAR(30) NOT NULL,
            des_prod VARCHAR(500) NOT NULL,
            proveedor VARCHAR(100) NOT NULL,
            categoria VARCHAR (100) NOT NULL,
            presentacion VARCHAR(30) NOT NULL,
            precio DECIMAL(10,2) NOT NULL)
            ''')
        self.conn.commit()

        
    #----------------------------------------------------------------
    def agregar_producto(self, id_prod, nombre_prod, des_prod, proveedor, categoria, presentacion, precio):
        # Verificamos si ya existe un producto con el mismo código
        self.cursor.execute(f"SELECT * FROM productos WHERE id_prod = {id_prod}")
        producto_existe = self.cursor.fetchone()
        if producto_existe:
            return False
        sql = "INSERT INTO productos (id_prod, nombre_prod, des_prod, proveedor, categoria, presentacion, precio) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        valores = (id_prod, nombre_prod, des_prod,proveedor,categoria, presentacion, precio)

        self.cursor.execute(sql, valores)        
        self.conn.commit()
        return True

    #----------------------------------------------------------------
    
    def consultar_producto(self, id_prod):
    #   # Consultamos un producto a partir de su código
        self.cursor.execute(f"SELECT * FROM productos WHERE id_prod = {id_prod}")
  
        return self.cursor.fetchone()



    #----------------------------------------------------------------
    def modificar_producto(self, id_prod, nuevo_nombre, nueva_descripcion, nuevo_proveedor, nueva_categoria, nueva_presentacion, nuevo_precio):
        sql = "UPDATE productos SET nombre_prod = %s, des_prod = %s,proveedor = %s,categoria = %s, presentacion = %s, precio = %s WHERE id_prod = %s"
        valores = (nuevo_nombre, nueva_descripcion, nuevo_proveedor, nueva_categoria, nueva_presentacion, nuevo_precio, id_prod)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    #----------------------------------------------------------------
    def listar_productos(self):
        self.cursor.execute("SELECT * FROM productos")
        productos = self.cursor.fetchall()
        return productos

    #----------------------------------------------------------------
    def eliminar_producto(self, id_prod):
        # Eliminamos un producto de la tabla a partir de su código
        self.cursor.execute(f"DELETE FROM productos WHERE id_prod = {id_prod}")
        self.conn.commit()
        return self.cursor.rowcount > 0

    #----------------------------------------------------------------
    def mostrar_producto(self, id_prod):

        producto = self.consultar_producto(id_prod)
        if producto:
            print("-" * 40)
            print(f"Código.....: {producto['id_prod']}")
            print(f"Nombre:....: {producto['nombre_prod']}")
            print(f"Descripción: {producto['des_prod']}")
            print(f"Proveedor..: {producto['proveedor']}")
            print(f"Categoria..: {producto['categoria']}")
            print(f"Presentacion: {producto['presentacion']}")
            print(f"Precio.....: {producto['precio']}")
    
            print("-" * 40)
        else:
            print("Producto no encontrado.")


#--------------------------------------------------------------------
# Cuerpo del programa
#--------------------------------------------------------------------
# Crear una instancia de la clase Catalogo

catalogo = Catalogo(host='localhost', user='root', password='', database='suplesport')

# Carpeta para guardar las imagenes.
#ruta_destino = './static/imagenes/'
#--------------------------------------------------------------------
@app2.route("/productos", methods=["GET"])
def listar_productos():
    productos = catalogo.listar_productos()
    return jsonify(productos)



#--------------------------------------------------------------------
@app2.route("/productos/<int:id_prod>", methods=["GET"])
def mostrar_producto(id_prod):
    producto = catalogo.consultar_producto(id_prod)
    if producto:
        return jsonify(producto)
    else:
        return "Producto no encontrado", 404

#--------------------------------------------------------------------

@app2.route("/productos", methods=["POST"])
def agregar_producto():
    id_prod = request.form['codigo']
    nombre_prod = request.form['nombre']
    des_prod = request.form['descripcion']
    proveedor = request.form['proveedor'] 
    categoria = request.form['categoria']  
    presentacion = request.form['presentacion']
    precio = request.form['precio']
    


    if catalogo.agregar_producto(id_prod, nombre_prod, des_prod, proveedor, categoria, presentacion, precio):
        return jsonify({"mensaje": "Producto agregado"}), 201
    else:
        return jsonify({"mensaje": "Producto ya existe"}), 400


#--------------------------------------------------------------------

@app2.route("/productos/<int:id_prod>", methods=["PUT"])
def modificar_producto(id_prod):
    # Procesamiento de la imagen
    #imagen = request.files['imagen']
    #nombre_imagen = secure_filename(imagen.filename)
    #print("*"*20)
    #print(nombre_imagen)
    #print("*"*20)
    #nombre_base, extension = os.path.splitext(nombre_imagen)
    #nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"
    #imagen.save(os.path.join(ruta_destino, nombre_imagen))

    # Datos del producto
    data = request.form
    nuevo_nombre = data.get("nombre")
    nueva_descripcion = data.get("descripcion")
    nuevo_proveedor = data.get("proveedor")
    nueva_categoria = data.get("categoria")
    nueva_presentacion = data.get("presentacion")
    nuevo_precio = data.get("precio")


    # Actualización del producto
    if catalogo.modificar_producto(id_prod, nuevo_nombre, nueva_descripcion, nuevo_proveedor, nueva_categoria, nueva_presentacion, nuevo_precio):
        return jsonify({"mensaje": "Producto modificado"}), 200
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 404


#--------------------------------------------------------------------

@app2.route("/productos/<int:id_prod>", methods=["DELETE"])
def eliminar_producto(id_prod):
    # Primero, obtén la información del producto para encontrar la imagen
    producto = catalogo.consultar_producto(id_prod)
    if producto:
        # Eliminar la imagen asociada si existe
        #ruta_imagen = os.path.join(ruta_destino, producto['imagen_url'])
        #if os.path.exists(ruta_imagen):
        #    os.remove(ruta_imagen)

        # Luego, elimina el producto del catálogo
        if catalogo.eliminar_producto(id_prod):
            return jsonify({"mensaje": "Producto eliminado"}), 200
        else:
            return jsonify({"mensaje": "Error al eliminar el producto"}), 500
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 404
#--------------------------------------------------------------------
# Consultamos un producto y lo mostramos
#producto = catalogo.mostrar_producto(22)



if __name__ == "__main__":
    app2.run(debug=True)





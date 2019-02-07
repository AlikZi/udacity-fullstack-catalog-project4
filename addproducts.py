'''
Insert data to the "furniturecatalog.db" database
'''


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Product, User

engine = create_engine('sqlite:///furniturecatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


user1 = User(name='Aleksandr Zonis', email='zonis7@gmail.com')
session.add(user1)
session.commit()


category1 = Category(name="Bedroom", user_id=user1.id)

session.add(category1)
session.commit()


product1 = Product(name="Queen Bed",
                   description="A clean design with solid wood veneer.\
                    Place the bed on its own or with the headboard against \
                    a wall. You also get spacious storage boxes that roll \
                    out smoothly om casters.",
                   image_url="https://www.ikea.com/us/en/images/products/"
                   "malm-high-bed-frame-storage-boxes__"
                   "0559914_PE662091_S4.JPG",
                   product_url="https://www.ikea.com/us/en/"
                   "catalog/products/S79157187/",
                   category_id=category1.id, user_id=user1.id)

session.add(product1)
session.commit()


product2 = Product(name="Single Bed",
                   description="Sustainable beauty from sustainably-sourced \
                                solid wood, a durable and renewable material \
                                that maintains its genuine character with \
                                each passing year. Combines with the other \
                                furniture in the HEMNES series.",
                   image_url="https://www.ikea.com/us/en/images/products/"
                   "hemnes-bed-frame__0555084_PE660120_S4.JPG",
                   product_url="https://www.ikea.com/us/en/catalog/"
                   "products/S09011674/",
                   category_id=category1.id, user_id=user1.id)

session.add(product2)
session.commit()


product3 = Product(name="Mattress",
                   description="Natural materials like natural latex, \
                                coconut fiber, cotton and wool provide \
                                comfort and pull away moisture. This makes \
                                for a pleasant sleeping environment with a \
                                cool and even sleep temperature.",
                   image_url="https://www.ikea.com/us/en/images/products/"
                   "holmsbu-pillowtop-mattress-white__0461385_"
                   "PE607520_S4.JPG",
                   product_url="https://www.ikea.com/us/en/"
                   "catalog/products/90386093/",
                   category_id=category1.id, user_id=user1.id)

session.add(product3)
session.commit()

product4 = Product(name="Chest Drawers",
                   description="Made of solid wood, which is a durable \
                                  and warm natural material.",
                   image_url="https://www.ikea.com/us/en/images/products/"
                   "hemnes-drawer-chest-brown__0559778_PE662026_S4.JPG",
                   product_url="https://www.ikea.com/us/en/catalog/"
                   "products/40392478/",
                   category_id=category1.id, user_id=user1.id)

session.add(product4)
session.commit()


product5 = Product(name="Night Stand",
                   description="Smooth running drawers with pull-out stop.",
                   image_url="https://www.ikea.com/us/en/images/products/"
                   "askvoll-drawer-chest-white__0651100_PE706668_S4.JPG",
                   product_url="https://www.ikea.com/us/en/catalog/"
                   "products/20270816/",
                   category_id=category1.id, user_id=user1.id)

session.add(product5)
session.commit()


product6 = Product(name="Bedspread",
                   description="Light Blue. Fleece is a soft, easy-care \
                                material that you can machine wash.",
                   image_url="https://www.ikea.com/us/en/images/products/"
                   "trattviva-bedspread-blue__0513134_PE639571_S4.JPG",
                   product_url="https://www.ikea.com/us/en/catalog/"
                   "products/20349339/",
                   category_id=category1.id, user_id=user1.id)

session.add(product6)
session.commit()


product7 = Product(name="Pillow",
                   description="An ergonomic pillow in lyocell and cotton \
                                fabric with polyester and lyocell blend \
                                comfortering and memory foam filling.",
                   image_url="https://www.ikea.com/us/en/images/products/"
                   "rolleka-memory-foam-pillow-white__0606844_"
                   "PE682578_S4.JPG",
                   product_url="https://www.ikea.com/us/en/catalog/"
                   "products/70269839/",
                   category_id=category1.id, user_id=user1.id)
session.add(product7)
session.commit()


category2 = Category(name="Living Room", user_id=user1.id)
session.add(category2)
session.commit()


product8 = Product(name="Sofa",
                   description="Cuddle up in the soft comfort of KIVIK \
                                sofa. The generous size, low armrests, \
                                and memory foam that adapts to the contours \
                                of your body invites many hours of naps, \
                                socializing, and relaxation.",
                   image_url="https://www.ikea.com/us/en/images/products/"
                   "kivik-sofa-red__0568414_PE667158_S4.JPG",
                   product_url="https://www.ikea.com/us/en/catalog/"
                   "products/S59252963/",
                   category_id=category2.id, user_id=user1.id)
session.add(product8)
session.commit()


product9 = Product(name="TV unit",
                   description="The TV bench in walnut veneer with legs of \
                                solid ash brings a warm, natural feeling to \
                                your room.",
                   image_url="https://www.ikea.com/us/en/images/products/"
                   "hemnes-tv-unit__0625361_PE692211_S4.JPG",
                   product_url="https://www.ikea.com/us/en/catalog/"
                   "products/60239715/",
                   category_id=category2.id, user_id=user1.id)
session.add(product9)
session.commit()

product10 = Product(name="Bookcase",
                    description="It is estimated that every five seconds, one \
                                BILLY bookcase is sold somewhere in the \
                                world. Pretty impressive considering we \
                                launched BILLY in 1979.",
                    image_url="https://www.ikea.com/us/en/images/products/"
                    "billy-bookcase-with-glass-doors-blue__"
                    "0429309_PE584188_S4.JPG",
                    product_url="https://www.ikea.com/us/en/catalog/"
                    "products/20323805/",
                    category_id=category2.id, user_id=user1.id)
session.add(product10)
session.commit()

user2 = User(name='Natalia Khirina', email='natalia.khirina@gmail.com')
session.add(user2)
session.commit()

category3 = Category(name="Kitchen", user_id=user2.id)
session.add(category3)
session.commit()

product11 = Product(name="Dinnerware Set",
                    description="The classic clean lines and the \
                                white stoneware helps FLITIGHET tableware \
                                suit most dishes and occasions. It is also \
                                easy to coordinate with your favorite \
                                tablecloth and glasses.",
                    image_url="https://www.ikea.com/us/en/images/products/"
                    "flitighet-piece-dinnerware-set-white__0629499_"
                    "PE694327_S4.JPG",
                    product_url="https://www.ikea.com/us/en/catalog/"
                    "products/50333921/",
                    category_id=category3.id, user_id=user2.id)
session.add(product11)
session.commit()

product12 = Product(name="Dining Table",
                    description="The solid oak top layer gives each table \
                                a unique character that you can feel proud \
                                of and live with for a long time. The plank \
                                feeling is achieved with modern production \
                                techniques that use less wood.",
                    image_url="https://www.ikea.com/us/en/images/products/"
                    "morbylanga-table__0533580_PE648686_S4.JPG",
                    product_url="https://www.ikea.com/us/en/catalog/"
                    "products/50386245/",
                    category_id=category3.id, user_id=user2.id)
session.add(product12)
session.commit()

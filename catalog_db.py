from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog_database_setup import Base, Categories, item
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
soccer = Categories(name='Soccer')
session.add(soccer)
session.commit()
myFirstCatalog = Categories(name='Basketball')
session.add(myFirstCatalog)
session.commit()
myFirstCatalog = Categories(name='Baseball')
session.add(myFirstCatalog)
session.commit()
myFirstCatalog = Categories(name='Frisbee')
session.add(myFirstCatalog)
session.commit()
snowBoarding = Categories(name='Snowboarding')
session.add(myFirstCatalog)
session.commit()
myFirstCatalog = Categories(name='Rock Climbing')
session.add(myFirstCatalog)
session.commit()
myFirstCatalog = Categories(name='Foosball')
session.add(myFirstCatalog)
session.commit()
myFirstCatalog = Categories(name='Skating')
session.add(myFirstCatalog)
session.commit()
myFirstCatalog = Categories(name='Hockey')
session.add(myFirstCatalog)

soccerItem1 = item(name='SoccerBall', items=soccer,
                   description=" one size fits all")
session.add(soccerItem1)
soccerItem2 = item(name='SoccerNet', items=soccer,
                   description="sturdy and grade A quality")
session.add(soccerItem2)
snowBoardingItem1 = item(name='Googles', items=snowBoarding,
                         description="Must be worn while snowboarding")
session.add(snowBoardingItem1)
snowBoardingItem2 = item(name='Snowboard', items=snowBoarding,
                         description="Best for any terrain and conditions")
session.add(snowBoardingItem2)
session.commit()

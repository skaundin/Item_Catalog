from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog_database_setup import Base, Category, Item
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

soccer = Category(name='Soccer')
session.add(soccer)

basketball = Category(name='Basketball')
session.add(basketball)

baseball = Category(name='Baseball')
session.add(baseball)

frisbee = Category(name='Frisbee')
session.add(frisbee)

snowBoarding = Category(name='Snowboarding')
session.add(snowBoarding)

rock_climbing = Category(name='Rock Climbing')
session.add(rock_climbing)

foosball = Category(name='Foosball')
session.add(foosball)

skating = Category(name='Skating')
session.add(skating)

hockey = Category(name='Hockey')
session.add(hockey)

soccerItem1 = Item(name='SoccerBall', category=soccer,
                   description=" one size fits all")
session.add(soccerItem1)
soccerItem2 = Item(name='SoccerNet', category=soccer,
                   description="sturdy and grade A quality")
session.add(soccerItem2)
snowBoardingItem1 = Item(name='Goggles', category=snowBoarding,
                         description="Must be worn while snowboarding")
session.add(snowBoardingItem1)
snowBoardingItem2 = Item(name='Snowboard', category=snowBoarding,
                         description="Best for any terrain and conditions")
session.add(snowBoardingItem2)
session.commit()

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from app.database import AsyncSessionLocal

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/seed")
async def seed_database():
    """Seed categories, menu items, and seats. Call once after first deploy."""
    async with AsyncSessionLocal() as db:
        # Categories
        cats = [
            ("breakfast", "早餐", "Breakfast", 1),
            ("mains", "主食", "Mains", 2),
            ("drinks", "饮料", "Drinks", 3),
            ("snacks", "小食", "Snacks", 4),
            ("desserts", "甜点", "Desserts", 5),
        ]
        for cat_id, name_zh, name_en, sort in cats:
            await db.execute(
                text("""
                    INSERT INTO categories (id, name_zh, name_en, sort_order, is_active)
                    VALUES (:id, :name_zh, :name_en, :sort_order, true)
                    ON CONFLICT (id) DO NOTHING
                """),
                {"id": cat_id, "name_zh": name_zh, "name_en": name_en, "sort_order": sort},
            )
        await db.commit()

        # Menu items
        items = [
            ("breakfast", "招牌早餐套餐", "Signature Breakfast Set", "烤面包+煎蛋+咖啡", "Toasted bread, fried egg, coffee", 8.80),
            ("breakfast", "牛油果吐司", "Avocado Toast", "全麦吐司配牛油果泥", "Wholemeal toast with smashed avocado", 7.50),
            ("breakfast", "美式早餐", "American Breakfast", "培根+煎蛋+烤面包+咖啡", "Bacon, fried egg, toast, coffee", 9.80),
            ("breakfast", "华夫饼套餐", "Waffle Set", "香草华夫饼+奶油+蜂蜜", "Vanilla waffle with cream and honey", 6.80),
            ("breakfast", "鲜榨果汁", "Fresh Juice", "橙/苹果/胡萝卜", "Orange/Apple/Carrot", 5.50),
            ("mains", "新加坡叻沙", "Singapore Laksa", "椰浆汤底配米粉、大虾、鱼丸", "Coconut broth, rice noodles, prawns, fish cake", 13.80),
            ("mains", "椰浆饭", "Nasi Lemak", "香米+椰浆+花生+参巴酱+煎蛋", "Fragrant rice, coconut milk, peanuts, sambal, fried egg", 12.50),
            ("mains", "福建炒虾面", "Hokkien Prawn Mee", "黄面+大虾+蒜蓉+葱", "Yellow noodles, prawns, garlic, spring onion", 14.00),
            ("mains", "鸡饭", "Hainanese Chicken Rice", "白斩鸡+香米+辣椒酱", "Poached chicken, fragrant rice, chili sauce", 11.80),
            ("mains", "肉骨茶", "Bak Kut Teh", "猪骨汤+蒜+胡椒+油条", "Pork rib soup, garlic, pepper, youtiao", 12.80),
            ("mains", "咖喱鱼头", "Curry Fish Head", "红鱼头+茄子+豆腐+椰浆", "Red snapper head, eggplant, tofu, coconut milk", 18.80),
            ("mains", "炒粿条", "Char Kway Teow", "flat noodles+虾+鸡蛋+腊肠", "Flat noodles, prawns, egg, Chinese sausage", 10.80),
            ("drinks", "新加坡司令", "Singapore Sling", "杜松子+樱桃白兰地+菠萝+柠檬", "Gin, cherry brandy, pineapple, lime", 12.00),
            ("drinks", "美式咖啡", "Americano", "双份浓缩+热水", "Double espresso, hot water", 4.50),
            ("drinks", "拿铁", "Café Latte", "浓缩+蒸奶", "Espresso, steamed milk", 5.50),
            ("drinks", "抹茶拿铁", "Matcha Latte", "抹茶+蒸奶+少许糖", "Matcha, steamed milk, light sugar", 6.00),
            ("drinks", "泰式奶茶", "Thai Milk Tea", "泰式红茶+淡奶+冰", "Thai black tea, evaporated milk, ice", 5.00),
            ("drinks", "柠檬茶", "Lemon Tea", "红茶+柠檬片+冰", "Black tea, lemon slice, ice", 4.00),
            ("drinks", "矿泉水", "Mineral Water", "瓶装 Evian/农夫山泉", "Bottled Evian/Nongfu Spring", 3.00),
            ("snacks", "沙爹串", "Satay Skewers", "鸡肉/羊肉4串+花生酱", "Chicken/Mutton 4pcs+peanut sauce", 8.80),
            ("snacks", "炸鸡翅", "Crispy Chicken Wings", "6只鸡翅+甜辣酱", "6pcs wings+sweet chili sauce", 9.80),
            ("snacks", "马来风光", "Sambal Kangkung", "空心菜+参巴酱+小鱼干", "Water spinach, sambal, anchovies", 7.50),
            ("snacks", "印度煎饼", "Roti Prata", "饼+咖喱汁", "Prata+curry dip", 4.50),
            ("snacks", "咖喱角", "Curry Puff", "土豆+鸡肉+咖喱馅", "Potato, chicken, curry filling", 3.50),
            ("desserts", "珍多冰", "Ice Kachang", "冰沙+红豆+椰奶+仙草", "Ice shave, red bean, coconut milk, grass jelly", 5.00),
            ("desserts", "榴莲珍多", "Durian Ice Kachang", "冰沙+榴莲肉+椰奶", "Ice shave, durian flesh, coconut milk", 8.50),
            ("desserts", "红豆冰", "Red Bean Ice", "冰沙+红豆+淡奶", "Ice shave, red bean, evaporated milk", 4.50),
            ("desserts", "雪媚娘", "Snow Skin Mochi", "4粒装+芒果/草莓/抹茶", "4pcs+mango/strawberry/matcha", 7.80),
            ("desserts", "提拉米苏", "Tiramisu", "经典意式+咖啡力娇酒", "Classic Italian with Kahlua", 9.00),
        ]

        for cat_id, name_zh, name_en, desc_zh, desc_en, price in items:
            await db.execute(
                text("""
                    INSERT INTO items (category_id, name_zh, name_en, description_zh,
                                       description_en, price_sgd, is_available, sort_order, is_active)
                    VALUES (:cat_id, :name_zh, :name_en, :desc_zh, :desc_en,
                            :price, true, 0, true)
                    ON CONFLICT DO NOTHING
                """),
                {"cat_id": cat_id, "name_zh": name_zh, "name_en": name_en,
                 "desc_zh": desc_zh, "desc_en": desc_en, "price": price},
            )
        await db.commit()

        # Seats
        seat_data = [
            ("T01","室内 01","Indoor 01","indoor"),("T02","室内 02","Indoor 02","indoor"),
            ("T03","室内 03","Indoor 03","indoor"),("T04","室内 04","Indoor 04","indoor"),
            ("T05","室内 05","Indoor 05","indoor"),("T06","室内 06","Indoor 06","indoor"),
            ("T07","室内 07","Indoor 07","indoor"),("T08","室内 08","Indoor 08","indoor"),
            ("T09","室内 09","Indoor 09","indoor"),("T10","室内 10","Indoor 10","indoor"),
            ("T11","室内 11","Indoor 11","indoor"),("T12","室内 12","Indoor 12","indoor"),
            ("O01","户外 01","Outdoor 01","outdoor"),("O02","户外 02","Outdoor 02","outdoor"),
            ("O03","户外 03","Outdoor 03","outdoor"),("O04","户外 04","Outdoor 04","outdoor"),
            ("B01","吧台 01","Bar 01","bar"),("B02","吧台 02","Bar 02","bar"),
            ("B03","吧台 03","Bar 03","bar"),("B04","吧台 04","Bar 04","bar"),
            ("B05","吧台 05","Bar 05","bar"),("B06","吧台 06","Bar 06","bar"),
        ]
        for seat_id, label_zh, label_en, zone in seat_data:
            await db.execute(
                text("""
                    INSERT INTO seats (id, label_zh, label_en, zone, status, is_active)
                    VALUES (:id, :label_zh, :label_en, :zone, 'vacant', true)
                    ON CONFLICT (id) DO NOTHING
                """),
                {"id": seat_id, "label_zh": label_zh, "label_en": label_en, "zone": zone},
            )
        await db.commit()

    return {"status": "seeded", "message": "Categories, menu items, and seats created"}

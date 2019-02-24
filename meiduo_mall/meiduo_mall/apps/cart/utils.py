# 封装合并购物车记录函数
import base64
import pickle

from django_redis import get_redis_connection


def merge_cookie_cart_to_redis(request, user, response):
    """将cookie中的购物车记录合并到登录用户的redis记录中"""
    cookie_cart = request.COOKIES.get('cart')

    if cookie_cart is None:
        # cookie购物车中无数据
        return

    # 解析cookie中的购物车数据
    cookie_dict = pickle.loads(base64.b64decode(cookie_cart))

    if not cookie_dict:
        # 字典未空,cookie购物车中无数据
        return

    # 2. 将cookie中购物车记录合并到登录用户的redis记录中

    # 存储cookie购物车记录中添加的商品id和对应数量count,此字典中的数据在进行购物车记录合并时需要设置到redis hash中
    cart = {}

    # 存储cookie中购物车记录中被勾选的商品的id,此列表中商品id在进行购物车记录合并时需要添加到redis set 中
    cart_selected_add = []

    # 存储cookie购物车记录中未被勾选商品的id,此列表中商品id在进行购物车记录合并时需要从redis set中移除
    cart_selected_remove = []

    for sku_id,count_selected in cookie_dict.items():
        cart[sku_id] = count_selected['count']

        if count_selected['selected']:
            # 勾选
            cart_selected_add.append(sku_id)
        else:
            # 未勾选
            cart_selected_remove.append(sku_id)

    # 合并
    redis_conn = get_redis_connection('cart')
    # 将cart字典中key和value作为属性和值设置到redis对应的hash元素中
    cart_key = 'cart_%s' % user.id
    redis_conn.hmset(cart_key, cart)

    # 将cart_selected_add中商品id添加到redis对应的色条元素中
    cart_selected_key = 'cart_selected_%s' % user.id

    if cart_selected_add:
        redis_conn.sadd(cart_selected_key, *cart_selected_add)

    # 将cart_selected_remove中商品的id从redis对应的set元素中移除
    if cart_selected_remove:
        redis_conn.srem(cart_selected_key, *cart_selected_remove)

    # 3. 删除cookie中购物车数据
    response.delete_cookie('cart')
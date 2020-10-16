"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyInteger, FuzzyChoice
from service.models import Wishlist, Item


class WishlistFactory(factory.Factory):
    """ Creates fake wishlist that you don't have to feed """

    class Meta:
        model = Wishlist

    id = factory.Sequence(lambda n: n+1)
    name = factory.Faker("name")
    user_id = FuzzyInteger(0, 1000)
    items = [Item(product_name='laptop', product_id=1), Item(product_name='iPhone', product_id=2)]


class ItemFactory(factory.Factory):
    """ Creates fake item that you don't have to feed """

    class Meta:
        model = Item

    id = factory.Sequence(lambda n: n+1)
    product_name = FuzzyChoice(choices=["samsung mobile", "wire", "other"])
    product_id = FuzzyInteger(0, 1000)


if __name__ == "__main__":
    for _ in range(10):
        wishlist = WishlistFactory()
        print(wishlist.serialize())

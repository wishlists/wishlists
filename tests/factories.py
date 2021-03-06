"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyInteger, FuzzyChoice
from service.models import Wishlist, Item


class WishlistFactory(factory.Factory):
    """ Creates fake wishlist that you don't have to feed """

    class Meta:
        """ Class that defines meta data """
        model = Wishlist

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    user_id = FuzzyInteger(0, 1000)


class ItemFactory(factory.Factory):
    """ Creates fake item that you don't have to feed """

    class Meta:
        """ Class that defines meta data """
        model = Item

    id = factory.Sequence(lambda n: n)
    product_name = FuzzyChoice(choices=["samsung mobile", "wire", "other"])
    product_id = FuzzyInteger(0, 1000)

from django.contrib import admin
from .models import Category, Customer,Product,Orders,Feedback, Supplier
from import_export.admin import ImportExportModelAdmin

# Register your models here.

from import_export import resources
from .models import Product

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'description', 'category', 'supplier', 'product_image')
        
class ProductImportExport(ImportExportModelAdmin):
    resource_class = ProductResource

class CustomerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Customer, CustomerAdmin)

admin.site.register(Supplier)



class ProductAdmin(admin.ModelAdmin):
    pass
admin.site.register(Product,ProductImportExport)

class OrderAdmin(admin.ModelAdmin):
    pass
admin.site.register(Orders, OrderAdmin)

class FeedbackAdmin(admin.ModelAdmin):
    pass
admin.site.register(Feedback, FeedbackAdmin)


class CategoryAdmin(admin.ModelAdmin):
    pass
admin.site.register(Category, CategoryAdmin)
# Register your models here.

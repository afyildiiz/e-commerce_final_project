from django.shortcuts import get_object_or_404, render,redirect,reverse
from . import forms,models
from django.http import HttpResponseRedirect,HttpResponse
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.conf import settings

def add_category_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin-categories')  # Redirect to the category list or some other page
    else:
        form = CategoryForm()
    return render(request, 'ecom/admin_add_category.html', {'form': form})

def home_view(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    product_count_in_cart = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'ecom/index.html', {'products': products, 'product_count_in_cart': product_count_in_cart, 'categories': categories})

# def product_list_by_category(request, category_id):
#     category = get_object_or_404(Category, id=category_id)
#     products = Product.objects.filter(category=category)
#     return render(request, 'ecom/product_list.html', {'category': category, 'products': products})
 
def product_list_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    context = {
        'category': category,
        'products': products,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'ecom/product_list.html', context)

#for showing login button for admin(by DOU)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')

# KULLANICI KAYIT
def customer_signup_view(request):
    userForm=forms.CustomerUserForm()
    customerForm=forms.CustomerForm()
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST)
        customerForm=forms.CustomerForm(request.POST,request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customer=customerForm.save(commit=False)
            customer.user=user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
        return HttpResponseRedirect('customerlogin')
    return render(request,'ecom/customersignup.html',context=mydict)

#----------- MUSTERİ OLUP OLMADIGINI KONTROL ETME FILTRESI
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()



#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,CUSTOMER
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    else:
        return redirect('admin-dashboard')

#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    # for cards on dashboard
    customercount=models.Customer.objects.all().count()
    productcount=models.Product.objects.all().count()
    ordercount=models.Orders.objects.all().count()

    # for recent order tables
    orders=models.Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_by=models.Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)

    mydict={
    'customercount':customercount,
    'productcount':productcount,
    'ordercount':ordercount,
    'data':zip(ordered_products,ordered_bys,orders),
    }
    return render(request,'ecom/admin_dashboard.html',context=mydict)


# admin view customer table
@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers=models.Customer.objects.all()
    return render(request,'ecom/view_customer.html',{'customers':customers})

# admin delete customer
@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')


@login_required(login_url='adminlogin')
def update_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('view-customer')
    return render(request,'ecom/admin_update_customer.html',context=mydict)

# admin view the product
@login_required(login_url='adminlogin')
def admin_products_view(request):
    products=models.Product.objects.all()
    return render(request,'ecom/admin_products.html',{'products':products})


# admin add product by clicking on floating button
@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    productForm=forms.ProductForm()
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
        return HttpResponseRedirect('admin-products')
    return render(request,'ecom/admin_add_products.html',{'productForm':productForm})


@login_required(login_url='adminlogin')
def delete_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')


@login_required(login_url='adminlogin')
def update_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    productForm=forms.ProductForm(instance=product)
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST,request.FILES,instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')
    return render(request,'ecom/admin_update_product.html',{'productForm':productForm})


@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    orders=models.Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_by=models.Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)
    return render(request,'ecom/admin_view_booking.html',{'data':zip(ordered_products,ordered_bys,orders)})


@login_required(login_url='adminlogin')
def delete_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')

# for changing status of order (pending,delivered...)
@login_required(login_url='adminlogin')
def update_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    orderForm=forms.OrderForm(instance=order)
    if request.method=='POST':
        orderForm=forms.OrderForm(request.POST,instance=order)
        if orderForm.is_valid():
            orderForm.save()
            return redirect('admin-view-booking')
    return render(request,'ecom/update_order.html',{'orderForm':orderForm})


# admin view the feedback
@login_required(login_url='adminlogin')
def view_feedback_view(request):
    feedbacks=models.Feedback.objects.all().order_by('-id')
    return render(request,'ecom/view_feedback.html',{'feedbacks':feedbacks})



#---------------------------------------------------------------------------------
#------------------------ PUBLIC CUSTOMER RELATED VIEWS START ---------------------
#---------------------------------------------------------------------------------
def search_view(request):
    # whatever user write in search box we get in query
    query = request.GET['query']
    products=models.Product.objects.all().filter(name__icontains=query)
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # word variable will be shown in html when user click on search button
    word="Searched Result :"

    if request.user.is_authenticated:
        return render(request,'ecom/customer_home.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart})
    return render(request,'ecom/index.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart})


from django.shortcuts import render, redirect
from django.contrib import messages
from . import models

def add_to_cart_view(request, pk):
    # Sepetteki ürünlerin sayısını ve tüm ürünleri veritabanından alır
    products = models.Product.objects.all()

    # Sepetteki ürünlerin kimliklerini çerezlerden okur
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0

    # Ürün kimliğini çerezlere ekler
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids == "":
            product_ids = str(pk)
        else:
            product_ids = product_ids + "|" + str(pk)
        response = redirect('customer-home')  # Ana sayfaya yönlendirir
        response.set_cookie('product_ids', product_ids)
    else:
        response = redirect('customer-home')  # Ana sayfaya yönlendirir
        response.set_cookie('product_ids', pk)

    # Eklenen ürün hakkında bilgi verir
    product = models.Product.objects.get(id=pk)
    messages.info(request, product.name + ' sepete başarıyla eklendi!')

    return response



# for checkout of cart
def cart_view(request):
    #for cart counter
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # fetching product details from db whose id is present in cookie
    products=None
    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Product.objects.all().filter(id__in = product_id_in_cart)

            #for total price shown in cart
            for p in products:
                total=total+p.price
    return render(request,'ecom/cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})


def remove_from_cart_view(request,pk):
    #for counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # removing product id from cookie
    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_id_in_cart=product_ids.split('|')
        product_id_in_cart=list(set(product_id_in_cart))
        product_id_in_cart.remove(str(pk))
        products=models.Product.objects.all().filter(id__in = product_id_in_cart)
        #for total price shown in cart after removing product
        for p in products:
            total=total+p.price

        #  for update coookie value after removing product id in cart
        value=""
        for i in range(len(product_id_in_cart)):
            if i==0:
                value=value+product_id_in_cart[0]
            else:
                value=value+"|"+product_id_in_cart[i]
        response = render(request, 'ecom/cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})
        if value=="":
            response.delete_cookie('product_ids')
        response.set_cookie('product_ids',value)
        return response


def send_feedback_view(request):
    feedbackForm=forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'ecom/feedback_sent.html')
    return render(request, 'ecom/send_feedback.html', {'feedbackForm':feedbackForm})


#---------------------------------------------------------------------------------
#------------------------ Müşteri İle İlgili Bölümler ------------------------------
#---------------------------------------------------------------------------------
# Bu fonksiyon, müşterinin giriş yapıp yapmadığını ve müşteri olup olmadığını kontrol eder.
# Ardından, tüm ürünleri veritabanından çeker ve sepet içindeki ürünlerin sayısını çerezlerden okur.
# Son olarak, bu bilgileri kullanarak customer_home.html şablonunu render eder.
from django.http import JsonResponse
from django.template.loader import render_to_string
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_home_view(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0
    return render(request, 'ecom/customer_home.html', {'categories': categories, 'products': products, 'product_count_in_cart': product_count_in_cart})

def ajax_filter_products(request):
    category_id = request.GET.get('category_id')
    query = request.GET.get('query')

    products = Product.objects.all()

    if category_id:
        products = products.filter(category_id=category_id)
    
    if query:
        products = products.filter(name__icontains=query)
    
    html = render_to_string('ecom/product_list.html', {'products': products})
    return JsonResponse({'data': html})


# sipariş öncesi tewslimat adresi
@login_required(login_url='customerlogin')
def customer_address_view(request):
    # this is for checking whether product is present in cart or not
    # if there is no product in cart we will not show address form
    product_in_cart=False
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_in_cart=True
    #for counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            # here we are taking address, email, mobile at time of order placement
            # we are not taking it from customer account table because
            # these thing can be changes
            email = addressForm.cleaned_data['Email']
            mobile=addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']
            #for showing total price on payment page.....accessing id from cookies then fetching  price of product from db
            total=0
            if 'product_ids' in request.COOKIES:
                product_ids = request.COOKIES['product_ids']
                if product_ids != "":
                    product_id_in_cart=product_ids.split('|')
                    products=models.Product.objects.all().filter(id__in = product_id_in_cart)
                    for p in products:
                        total=total+p.price

            response = render(request, 'ecom/payment.html',{'total':total})
            response.set_cookie('email',email)
            response.set_cookie('mobile',mobile)
            response.set_cookie('address',address)
            return response
    return render(request,'ecom/customer_address.html',{'addressForm':addressForm,'product_in_cart':product_in_cart,'product_count_in_cart':product_count_in_cart})




# burada sadece bu görünüme yöneliyoruz...aslında ödemenin başarılı olup olmadığını kontrol etmemiz gerekiyor
# o zaman yalnızca bu görünüme erişilmelidir
@login_required(login_url='customerlogin')
def payment_success_view(request):
    # Burada sipariş vereceğiz | başarılı ödeme sonrasında
    # müşterinin cep telefonunu, adresini, E-postasını alacağız
    # ürün kimliğini çerezlerden alacağız, ardından ilgili ayrıntıları db'den alacağız
    # daha sonra sipariş nesneleri oluşturacağız ve veritabanında saklayacağız
    # bundan sonra çerezleri sileceğiz çünkü sipariş verildikten sonra...sepetin boş olması gerekir
    customer=models.Customer.objects.get(user_id=request.user.id)
    products=None
    email=None
    mobile=None
    address=None
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Product.objects.all().filter(id__in = product_id_in_cart)
            # Burada tek seferde bir müşteri tarafından sipariş edilecek ürünlerin listesini alıyoruz

 #bu şeyler değişiklik gösterebilir, sipariş anında erişebilirsiniz...
    if 'email' in request.COOKIES:
        email=request.COOKIES['email']
    if 'mobile' in request.COOKIES:
        mobile=request.COOKIES['mobile']
    if 'address' in request.COOKIES:
        address=request.COOKIES['address']

    # burada ürün sayısı kadar sipariş veriyoruz
    # diyelim ki sepetimizde 5 ürün var ve sipariş veriyoruz... yani siparişler tablosunda 5 satır oluşacak
    # Sipariş tablosunda çok fazla gereksiz veri olacak... ancak bunu normalleştirirsek daha karmaşık hale gelir
    for product in products:
        models.Orders.objects.get_or_create(customer=customer,product=product,status='Pending',email=email,mobile=mobile,address=address)

    # sipariş verildikten sonra çerezler silinmelidir
    response = render(request,'ecom/payment_success.html')
    response.delete_cookie('product_ids')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response




@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_order_view(request):
    
    customer=models.Customer.objects.get(user_id=request.user.id)
    orders=models.Orders.objects.all().filter(customer_id = customer)
    ordered_products=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_products.append(ordered_product)

    return render(request,'ecom/my_order.html',{'data':zip(ordered_products,orders)})
 



# @login_required(login_url='customerlogin')
# @user_passes_test(is_customer)
# def my_order_view2(request):

#     products=models.Product.objects.all()
#     if 'product_ids' in request.COOKIES:
#         product_ids = request.COOKIES['product_ids']
#         counter=product_ids.split('|')
#         product_count_in_cart=len(set(counter))
#     else:
#         product_count_in_cart=0
#     return render(request,'ecom/my_order.html',{'products':products,'product_count_in_cart':product_count_in_cart})    



#--------------for discharge patient bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def download_invoice_view(request,orderID,productID):
    order=models.Orders.objects.get(id=orderID)
    product=models.Product.objects.get(id=productID)
    mydict={
        'orderDate':order.order_date,
        'customerName':request.user,
        'customerEmail':order.email,
        'customerMobile':order.mobile,
        'shipmentAddress':order.address,
        'orderStatus':order.status,

        'productName':product.name,
        'productImage':product.product_image,
        'productPrice':product.price,
        'productDescription':product.description,


    }
    return render_to_pdf('ecom/download_invoice.html',mydict)





# PROFİL BİLGİLERİNİ GETİRME
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'ecom/my_profile.html',{'customer':customer})


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return HttpResponseRedirect('my-profile')
    return render(request,'ecom/edit_profile.html',context=mydict)



#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START --------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    categories = Category.objects.all()
    return render(request,'ecom/aboutus.html', {categories:"categories"})

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'ecom/contactussuccess.html')
    return render(request, 'ecom/contactus.html', {'form':sub})


#-----------------------Supplier Table----------------------##
#-----------------------------------------------------------##

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CategoryForm, CustomerForm
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import Category, Supplier




from django.shortcuts import render, redirect
from django.contrib.auth import  login, logout
from django.contrib import messages
from .models import Supplier

def supplier_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        if Supplier.objects.filter(email=email).exists():
            messages.error(request, 'Email is already taken')
            return redirect('supplier_signup')

        supplier = Supplier.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=password
        )

        messages.success(request, 'Account created successfully. Please log in.')
        return redirect('supplier_login')

    return render(request, 'ecom/suppliersignup.html')





from django.shortcuts import render, redirect
from django.contrib import messages, auth
from .models import Supplier, Product
from .forms import ProductForm


def supplier_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = Supplier.objects.get(email=email)
        except Supplier.DoesNotExist:
            messages.error(request, 'Invalid Email')
            return redirect('/supplierlogin/')

        # Check if the password matches
        if user.password == password:
            # Store supplier information in the session
            request.session['supplier_id'] = user.id
            messages.success(request, 'Logged in successfully.')
            return redirect('/supplierdasboard/')
        else:
            messages.error(request, 'Invalid Password')
            return redirect('/supplierlogin/')

    return render(request, 'ecom/supplierlogin.html')

def supplier_logout(request):
    # Clear the supplier information from the session
    request.session.pop('supplier_id', None)
    messages.success(request, 'Logged out successfully.')
    return redirect('/')  # Change 'index' to your desired homepage



def supplier_dasboard(request):
    # Check if the supplier is logged in
    supplier_id = request.session.get('supplier_id')
    if not supplier_id:
        messages.error(request, 'Please log in to view the dashboard.')
        return redirect('/login/')  # Adjust the login URL as needed

    # Fetch the supplier's products
    records = Product.objects.filter(supplier_id=supplier_id)

    mydict = {'records': records}
    return render(request, 'ecom/supplierdasboard.html', context=mydict)



from django.shortcuts import render, redirect
from .forms import ProductForm
from .models import Product

def add_product(request):
    # Check if the supplier is logged in
    supplier_id = request.session.get('supplier_id')
    if not supplier_id:
        messages.error(request, 'Please log in to add a product.')
        return redirect('/login/')  # Adjust the login URL as needed

    form = ProductForm(request.POST or None, request.FILES or None)
    
    if request.method == 'POST':
        if form.is_valid():
            # Set the supplier for the product before saving
            product = form.save(commit=False)
            product.supplier_id = supplier_id
            product.save()
            return redirect('/supplierdasboard/')

    mydict = {'form': form}
    return render(request, 'ecom/supplieraddproduct.html', mydict)



def add_edit(request,id=None):
    one_rec=Product.objects.get(pk=id)
    form=ProductForm(request.POST or None,request.FILES or None, instance=one_rec)
    if form.is_valid():
        form.save()
        return redirect('/supplierdasboard/')
    mydict= {'form':form}
    return render(request,'ecom/suppliereditproduct.html',context=mydict)

def add_delete(request,eid=None):
    one_rec = Product.objects.get(pk=eid)
    if  request.method=="POST":
         one_rec.delete()
         return redirect('/supplierdasboard/')
    return render(request,'ecom/supplierdeleteproduct.html')

def add_view(request,eid=None):
    mydict={}
    one_rec = Product.objects.get(pk=eid)
    mydict['user']=one_rec
    return render(request,'''ecom/supplierviewproduct.html''',mydict)


# admin view customer table
@login_required(login_url='adminlogin')
def view_supplier_view(request):
    customers=models.Supplier.objects.all()
    return render(request,'ecom/view_supplier.html',{'customers':customers})



# admin delete customer
@login_required(login_url='adminlogin')
def delete_supplier_view(request, pk):
    customer = Supplier.objects.get(id=pk)
    customer.delete()
    return redirect('view-supplier')


from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Supplier
from .forms import SupplierForm

@login_required(login_url='adminlogin')
def update_supplier_view(request, pk):
    supplier = Supplier.objects.get(id=pk)
    supplierForm = SupplierForm(instance=supplier)

    if request.method == 'POST':
        supplierForm = SupplierForm(request.POST, instance=supplier)
        if supplierForm.is_valid():
            # Check if the password field is in the cleaned_data
            if 'password' in supplierForm.cleaned_data:
                # If yes, hash the password and set it in the model
                supplierForm.cleaned_data['password'] = make_password(supplierForm.cleaned_data['password'])

            supplier = supplierForm.save()
            return redirect('view-supplier')

    mydict = {'supplierForm': supplierForm}
    return render(request, 'ecom/admin_update_supplier.html', context=mydict)




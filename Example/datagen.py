import numpy as np
import wavelet_transforms as wts
from nonguassianextraction import coherent_extraction
import fbm2d as fbm
import matplotlib.pyplot as plt

#Some original function definitions are here.
#The Powerlawmod functions are the same as in their original code in the repository.
#Running eGRF_save() creates and saves eGRF image to be used
#all_images() generates images of the modification increment-wise to show the change
#an example gif that was created is also included in the folder

#qfunction was used to determine the best threshold for coherent extraction

def powerlawmod(wt, wtC, tab_k,  wherestart, slope,):   
    
    
    Wc=abs(wtC)
    wtmod=np.zeros((wt.shape[0],wt.shape[1],wt.shape[2]))
    x=np.log(tab_k)
    awt=wtC.copy()
    awt=abs(awt)
    wt=abs(wt)

    power=np.log(np.mean((abs(wt)**2.), axis=(0,1)))
    powernew=np.log(np.mean((abs(Wc)**2.), axis=(0,1)))

    end=wtmod.shape[2]
   
    for i in range(int(wherestart-6),end):
        test=0
        ctest=0
        wtfori=abs(Wc[:,:,i])
       

        difference = slope * ( x[i] - x[wherestart] ) - powernew[i] + power[wherestart]

        constant= np.sqrt(np.exp(difference))
        
        wtmod[:,:,i]=wtfori*constant
     
    return wtmod


def interceptmod(wt, wtC, tab_k,  incr,):   
    
    
    Wc=abs(wtC)
    wtmod=np.zeros((wt.shape[0],wt.shape[1],wt.shape[2]))
    x=np.log(tab_k)
    awt=wtC.copy()
    awt=abs(awt)
    wt=abs(wt)

    power=np.log(np.mean((abs(wt)**2.), axis=(0,1)))
    powernew=np.log(np.mean((abs(Wc)**2.), axis=(0,1)))

    end=wtmod.shape[2]
   
    for i in range(end):
        wtfori=abs(Wc[:,:,i])
       

        difference = incr

        constant= np.sqrt(np.exp(difference))
        
        wtmod[:,:,i]=wtfori*constant
     
    return wtmod



def eGRF_save():
    image=fbm.fbm2d(-3.2,512,512)
    X0=np.std(image)
    #M=1.1
    #L=((np.log(1.+0.5*(M**2.)))**0.5)/X0
    L=1.5
    image=np.exp(L*image)
    image=image-image.min()

    wt,Wn,Wc, tab_k, S1ac, S1a= coherent_extraction(image, q=3.)
    Wc=np.sum(Wc[:], axis=3)


    np.save('/home/aparker/pycodes/data/image', image)
    np.save('/home/aparker/pycodes/data/wt',wt)
    np.save('/home/aparker/pycodes/data/Wn', Wn)
    np.save('/home/aparker/pycodes/data/Wc',Wc)
    np.save('/home/aparker/pycodes/data/tab_k',tab_k)
    np.save('/home/aparker/pycodes/data/S1ac',S1ac)
    np.save('/home/aparker/pycodes/data/S1a',S1a)

def q_test():
    image=fbm.fbm2d(-3.2,256,256)
    X0=np.std(image)
    #M=1.1
    #L=((np.log(1.+0.5*(M**2.)))**0.5)/X0
    L=1.5
    image=np.exp(L*image)
    image=image-image.min()
    for i in range(6):
        step=i*.4
        print step
        wt,Wn,Wc, tab_k, S1ac, S1a= coherent_extraction(image, q=step+2.)
        plt.figure(i)
        plt.hist(Wn.real[:,:,17].flatten(), bins=25)
        print Wn.shape
        
def all_images():
    

    image = np.load('/home/aparker/pycodes/data/image.npy')
    wt = np.load('/home/aparker/pycodes/data/wt.npy')
    Wn = np.load('/home/aparker/pycodes/data/Wn.npy')
    Wc = np.load('/home/aparker/pycodes/data/Wc.npy')
    tab_k = np.load('/home/aparker/pycodes/data/tab_k.npy')
    S1ac = np.load('/home/aparker/pycodes/data/S1ac.npy')
    S1a = np.load('/home/aparker/pycodes/data/S1a.npy')
    wt=np.complex128(wt)
    Wn=np.complex128(Wn)
    Wc=np.complex128(Wc)
    cphase=np.arctan2(Wc.imag, Wc.real)
    nphase=np.arctan2(Wn.imag,Wn.real)

    x=np.log(tab_k)
    power=np.log(np.mean((abs(wt)**2.), axis=(0,1), dtype=np.float64))
    powernew=np.log(np.mean((abs(Wc)**2.), axis=(0,1), dtype=np.float64))
    

    difference = abs(np.nanmean(powernew[15] - power[15]))
    
    incrementsize = difference / 25.
    wtnew=Wn.real.copy()
    Wc=powerlawmod(abs(wt),abs(Wc),tab_k, int(tab_k.shape[0]*1/2) , -3.3)
    Wc=interceptmod(abs(wt), abs(Wc), tab_k, -difference)

    

#Raising Power#
    for i in range(25):
        plt.close()
        f_fig, f_ax = plt.subplots(2, 1, figsize=(18,18))
        f_ax[0].set_xlim(-6,0)
        f_ax[0].set_ylim(-6,14)
        
        
        wtnew=0
        wCmod=0
        wCmod=interceptmod(abs(wt), abs(Wc), tab_k, incrementsize*(i))
        wCmod[np.isnan(wCmod)]=0
        wtnew=Wn.real+abs(wCmod)*np.cos(cphase)
        rec_image= wts.halo_inverse(wtnew, tab_k)
        y_c=np.log(np.mean((abs(wCmod)**2.), axis=(0,1)))
        
        f_ax[0].plot(x, y_c)
        f_ax[0].plot(x,power)
        f_ax[1].imshow(rec_image.real, interpolation='none', cmap= 'Greys_r',)
        f_ax[0].set_xlim(-6,0)
        f_ax[0].set_ylim(-6,14) 
    
        
       
        f_fig.savefig('/home/aparker/pycodes/data/modified_images/increment_'+str(i)+'.png')
        


#Changing Slopes
    for i in range(25):
        imagecount=i+24
        
        f_fig, f_ax = plt.subplots(2, 1, figsize=(18,18))
        
        frac_i= (i)/25.
        wCmod=0
        wCmod=powerlawmod(abs(wt),abs(Wc),tab_k, int(tab_k.shape[0]*1/2) , -3.3+frac_i)
    
        wCmod[np.isnan(wCmod)]=0
        wtnew=Wn.real+abs(wCmod)*np.cos(cphase)
        rec_image=wts.halo_inverse(wtnew,tab_k)
        y_c=np.log(np.mean((abs(wCmod)**2.), axis=(0,1)))
        
    
        f_ax[0].plot(x, y_c)
        f_ax[0].plot(x,power)
        f_ax[1].imshow(rec_image.real, interpolation='none', cmap= 'Greys_r')
        f_ax[0].set_xlim(-6,0)
        f_ax[0].set_ylim(-6,14)
       
        f_fig.savefig('/home/aparker/pycodes/data/modified_images/increment_'+str(imagecount)+'.png')
       
  


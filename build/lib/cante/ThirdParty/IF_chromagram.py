from numpy import arange, cos, pi, sin, zeros, hstack, vstack, where
from numpy import transpose, asarray, array, real, imag, shape, abs
from numpy import dot, floor, round, mean, power, log
from numpy.matlib import repmat
from scipy import fft, fftpack

def octs2hz (octs,fT):
    hz = fT/16.0*power(2,octs)
    return hz

def hz2octs(freq,fT):
    octs = log(freq/(fT/16.0))/log(2)
    return octs

def IF_chromagram(w,fT):
    '''
    THIS FUNCTION WAS PORTED FROM THE LabROSA-coversongID MATLAB IMPLEMENTATION WITH MINOR
    MODIFICATIONS.
    See http://labrosa.ee.columbia.edu/projects/coversongs/chromagram_IF.m.html for details.
    Copyright (c) 2006 Columbia University.

    :param w: audio samples with fs 44.1kHz
    :param fT: A4 tuning frequency
    :return: array holding the average chroma bin energies
    '''

    # INIT
    fftSize = 2048
    f_ctr = 1000.0
    f_sd = 1
    nchr = 12

    fminl = octs2hz(hz2octs(f_ctr,fT)-2*f_sd,fT)
    fminu = octs2hz(hz2octs(f_ctr,fT)-f_sd,fT)
    fmaxl = octs2hz(hz2octs(f_ctr,fT)+f_sd,fT)
    fmaxu = octs2hz(hz2octs(f_ctr,fT)+2*f_sd,fT)

    # IF-gram
    N = fftSize
    W = fftSize / 2
    H = fftSize / 4
    X = w
    s = len(X)
    sr = 44100

    nhops = 1 + int(float(s-W)/float(H))
    nmw1 = int(float(N-W)/2.0)
    nmw2 = int(N-W - nmw1)
    ww = 2.0 * pi * arange(N)*float(sr)/float(N)

    D = []
    F = []

    win = 0.5 * (1-cos(arange(W)/float(W)*2.0*pi))
    T =float(W)/float(sr)
    dwin = -pi / T * sin(arange(W)/float(W)*2.0*pi)
    norm = 2.0/sum(win)
    numSkipped = 0

    for h in range(0,nhops):
        u = X[int((h-1)*H) + arange(1,int(W+1))]
        if sum(u)==0:
            numSkipped = numSkipped + 1
            continue
        wu = win * u
        du = dwin * u
        wu = hstack((zeros((1,nmw1))[0],wu,zeros((1,nmw2))[0]))
        du = hstack((zeros((1,nmw1))[0],du,zeros((1,nmw2))[0]))
        t1 = fft(fftpack.fftshift(du))
        t2 = fft(fftpack.fftshift(wu))
        t22 = (t2[1:1+int(N/2)])*norm
        D.append(t22)
        t = array(t1 + (ww*t2)*1j,dtype=complex)
        a = real(t2)
        b = imag(t2)
        da = real(t)
        db = imag(t)
        instf = (1.0/(2.0*pi))*(a*db - b*da)/(a*a + b*b)
        F.append(instf[1:(1+int(N/2))])

    nhops = nhops-numSkipped
    D = asarray(D,dtype=complex)
    S = transpose(D)
    F = asarray(F,dtype=float)
    I = transpose(F)

    # IF pitch track
    maxbin = int(round(fmaxu * (float(fftSize)/float(sr))))

    ddiffA = vstack((I[1:maxbin,:],I[maxbin,:]))
    ddiffB = vstack((I[0,:],I[0:maxbin-1,:]))
    ddiff = ddiffA - ddiffB

    dgood = ddiff < 0.75 * float(sr)/float(fftSize)

    A = vstack((dgood[1:maxbin,:],dgood[maxbin-1,:]))
    A = A > 0
    B = vstack(([dgood[0,:],dgood[0:(maxbin-1),:]]))
    B = B > 0
    M = A | B
    dgood = dgood * M
    dgood = array(dgood,dtype=int)

    p = 0.0*dgood
    m = 0.0*dgood

    for t in range(0,nhops):
        ds = dgood[:,t]
        lds = len(ds)
        a = hstack(([0],ds[0:lds-1]))
        st = where((a==0) & (ds>0))
        st = st[0]
        b = hstack((ds[1:lds],[0]))
        en = where((ds>0) & (b == 0))
        en = en[0]
        npks = len(st)
        frqs = []
        mags = []
        for i in range(0,npks):
            bump = abs(S[st[i]:en[i],t])
            if len(bump)==0:
                frqs.append(0.0)
                mags.append(0.0)
                continue
            div = sum(bump)
            div += sum(bump==0)*1.0
            frqs.append(dot(bump,I[st[i]:en[i],t])/float(div))
            mags.append(sum(bump))
            if frqs[i] > fmaxu:
                mags[i] = 0
                frqs[i] = 0
            elif frqs[i] > fmaxl:
                mags[i] = mags[i] * max((0, (fmaxu-frqs[i])/(fmaxu-fmaxl)))
            if frqs[i] < fminl:
                mags[i] = 0
                frqs[i] = 0
            elif frqs[i] < fminu:
                mags[i] = mags[i] * (frqs[i] - fminl)/(fminu-fminl)
            if frqs[i] < 0:
                mags[i] = 0
                frqs[i] = 0

        bin = (st+en)/2.0
        count = 0
        # TO DO:::: m looks weird....
        for b in bin:
            b = int(round(b))
            p[b,t] = frqs[count]
            m[b,t] = mags[count]
            count += 1

    ncols = shape(p)[1]
    Pocts = hz2octs(p+(p==0),fT)
    nzp = where(p[:]>0)
    Pocts[p[:]==0] = 0
    PoctsQ = array(Pocts)
    PoctsQ[nzp] = round(float(nchr)*Pocts[nzp])/float(nchr)
    Pmapc = round(float(nchr)*(PoctsQ - floor(PoctsQ)))
    Pmapc[p[:] == 0] = -1
    Pmapc[Pmapc[:] == nchr] = 0

    Y = zeros((nchr, ncols))
    for t in range(0,ncols):
        a = arange(0,nchr)
        b = shape(Pmapc)[0]
        z = repmat(a,b,1)
        z = transpose(z)
        zz = repmat(Pmapc[:,t],nchr,1)
        Y[:,t] = dot((z == zz), m[:,t])

    C = mean(Y,axis=1)
    C = C/max(C)

    return C

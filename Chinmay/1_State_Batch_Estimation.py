# -*- coding: utf-8 -*-
"""1_Batch_Estimation.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/19LEOj0RxAXRugV8ScMO1QN5aFeruB1-r
"""

!pip install casadi

## Importing external modules

import numpy as np
import matplotlib.pyplot as plt

from casadi import *

## Initial Setup

# State/Parameter/Output Dimensions
State_n = 1
Parameter_n = 5
Output_n = 1

# Initial Filter stae mean/covariance
T_ave  = 0

R_win = 0
C_in = 0
C1 = 0
C2 = 0
C3 = 0

# State Covariance
P_model = 1

# Filter process/measurement noise covariances
Q_model = 0.01
Q_params = 0.01
R_model = 0.01

# Creating Infinity
Infinity = np.inf

## Getting total time steps
N = y_measured.shape[0]

## Creating Optimization Variables

# State Variables
T_ave_l = SX.sym('T_ave',N,1)


# Parameter Variables
R_win = SX.sym('R_win',N,1)
C_in = SX.sym('C_in',N,1)
C1 = SX.sym('C1',N,1)
C2 = SX.sym('C2',N,1)
C3 = SX.sym('C3',N,1)


# Other Variables
v_l = SX.sym('v_l',N,1)
w_T_ave_l = SX.sym('w_T_ave_l',N-1,1)

## Constructing the Cost Function

# Constructing P_1_0 Matrix
P_1_0_inv = np.reshape(np.diag(np.reshape((1/P_model)*np.ones(State_n,),(State_n,)),k=0),(State_n,State_n))

##########################################
# Constructing Intermediate Variables
X_1_e = vcat([T_ave_l[0]] - (T_ave))

w_l = vcat([w_T_ave_l])

# Cost Function Development
CostFunction = 0

#Final Cost Function
# c X_1_e_T * P_1_0_inv * X_1_e
CostFunction += X_1_e.T @ P_1_0_inv @ X_1_e

## Constructing the Constraints

# Initializing Lower-Upper Bounds for State/Parameters/Intermediate variables and the Equations

T_ave_lb  = [0]
T_ave_ub  = [np.inf]

R_win_lb = [0]
R_win_ub = [np.inf]

C_in_lb= [0]
C_in_ub = [np.inf]

C1_lb = [0]
C1_ub = [np.inf]

C2_lb = [0]
C2_ub = [np.inf]

C3_lb = [0]
C3_ub = [np.inf]

v_lb = []
v_ub = []

w_T_ave_lb = []
w_T_ave_ub = []

Eq_T_ave_lb = []
Eq_R_win_lb = []
Eq_C_in_lb = []
Eq_C1_lb = []
Eq_C2_lb = []
Eq_C3_lb = []
Eq_y_lb = []

Eq_T_ave_ub = []
Eq_R_win_lb = []
Eq_C_in_lb = []
Eq_C1_lb = []
Eq_C2_lb = []
Eq_C3_lb = []
Eq_y_ub = []

# staking equations
Eq_T_ave = []
Eq_R_win = []
Eq_C_in = []
Eq_C1 = []
Eq_C2 = []
Eq_C3 = []
Eq_y = []

# FOR LOOP: For each time step
for ii in range(N):

    # Computing Cost Function: v_l_T * R_inv * v_l
    CostFunction += v_l[ii]**2 * (1/R_model)

    if (ii < N-1):

        # Computing Cost Function: w_l_T * Q_inv * w_l
        CostFunction += w_T_ave_l[ii]**2 * (1/Q_model)

        # State Equations - Formulation
###############################################################
        ## ORIGINAL: x1_Eq = -x1_l[ii+1] + x1_l[ii] + ts*(x2_l[ii]) + w_x1_l[ii]

        #SUBSTITUTE : x2_l[ii] = (1/(C_in) * ( (T_am[ii] - Tave[ii+1]/ (R_win )) + C1*Q_int[ii] + C2*Q_ac[ii] + C3*Q_sol[ii] + Q_venti[ii] + Q_infi[ii]))

        T_ave_Eq = -T_ave_l[ii+1] + T_ave_l[ii] + ts*( (1/(C_in) * ( (T_am[ii] - Tave[ii+1]/ (R_win )) + C1*Q_int[ii] + C2*Q_ac[ii] + C3*Q_sol[ii] + Q_venti[ii] + Q_infi[ii])) ) + w_T_ave_l[ii]


       # Adding current equations to Equation List
        Eq_T_ave += [T_ave_Eq]


        # Adding Equation Bounds
        Eq_T_ave_lb += [0]

        Eq_T_ave_ub += [0]


        # Adding Variable Bounds
        w_T_ave_lb += [-Infinity]
        w_T_ave_ub += [Infinity]


    # Output Equations - Formulation
    #Equation remains same for 1/2/4
    y_Eq = -v_l[ii] + y_measured[ii] - T_ave_l[ii]

    # Adding current equations to Equation List
    Eq_y += [y_Eq]

    # Adding Equation Bounds
    Eq_y_lb += [0]

    Eq_y_ub += [0]

    # Adding Variable Bounds
    T_ave_lb += [-Infinity]
    T_ave_ub += [Infinity]


    v_lb += [-Infinity]
    v_ub += [Infinity]

## Constructing NLP Problem

# Creating Optimization Variable: x
x = vcat([T_ave_l, v_l, w_T_ave_l, R_win , C_in , C1 , C2 , C3 ])

# Creating Cost Function: J
J = CostFunction

# Creating Constraints: g
g = vertcat(*Eq_T_ave, *Eq_y)

# Creating NLP Problem
NLP_Problem = {'f': J, 'x': x, 'g': g}

## Constructiong NLP Solver
NLP_Solver = nlpsol('nlp_solver', 'ipopt', NLP_Problem)

## Solving the NLP Problem

# Creating Initial Variables
T_ave_l_ini = (T_ave * np.ones((N+1))).tolist()

R_win_l_ini = (R_win * np.ones((N+1))).tolist()
C_in_l_ini = (C_in * np.ones((N+1))).tolist()
C1_l_ini = (C1 * np.ones((N+1))).tolist()
C2_l_ini = (C2 * np.ones((N+1))).tolist()
C3_l_ini = (C3 * np.ones((N+1))).tolist()

v_l_ini = np.zeros((N,)).tolist()
w_T_ave_l_ini = np.zeros((N-1,)).tolist()



x_initial = vertcat(*T_ave_l_ini,  *R_win_l_ini, *C_in_l_ini, *C1_l_ini, *C2_l_ini, *C3_l_ini, v_l_ini, *w_T_ave_l_ini)


# Creating Lower/Upper bounds on Variables and Equations
x_lb = vertcat(*T_ave_lb, *R_win_lb, *C_in_lb, *C1_lb, *C2_lb, *C3_lb, *v_lb, *w_T_ave_lb )

x_ub = vertcat(*T_ave_ub, *R_win_ub, *C_in_ub, *C1_ub, *C2_ub, *C3_ub, *v_ub, *w_T_ave_ub )

G_lb = vertcat(*Eq_T_ave_lb, *Eq_y_lb)

G_ub = vertcat(*Eq_T_ave_ub, *Eq_y_ub)

# Solving NLP Problem
NLP_Solution = NLP_Solver(x0 = x_initial, lbx = x_lb, ubx = x_ub, lbg = G_lb, ubg = G_ub)

#----------------------------------------------------------------Solution Analysis ----------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------------------------------------------------#

## Getting the Solutions
NLP_Sol = NLP_Solution['x'].full().flatten()

T_ave_sol = NLP_Sol[0:N]

R_win_sol = NLP_Sol[N:2*N]
C_in_sol = NLP_Sol[2*N:3*N]
C1_sol = NLP_Sol[3*N:4*N]
C2_sol = NLP_Sol[4*N:5*N]
C3_sol = NLP_Sol[5*N:6*N]

##################################################
v_sol = NLP_Sol[6*N:7*N]
w_T_ave_sol = NLP_Sol[7*N:6*N-1]


## Simulation Plotting
# Setting Figure Size
plt.rcParams['figure.figsize'] = [Plot_Width, Plot_Height]

# Plotting Figures
plt.figure()

# Plotting  States
plt.plot(time_vector, T_ave_sol[0:-1].transpose(), label=r'$\ T_ave $ $(rads)$')
plt.xlabel('Time ' + r'$(sec)$', fontsize=12)
plt.ylabel('States '+ r'$(x)$', fontsize=12)
plt.title('Building States - NLP Solution ' + r'x', fontsize=14)
plt.legend(loc='upper right')
plt.tight_layout()
plt.grid(True)

# Plotting Figures
plt.figure()

# Plotting  Parameters - R_win -  of Nonlinear System
plt.subplot(211)
plt.plot(time_vector, R_win_sol*np.ones((np.shape(time_vector)[0],1)), label=r'$R_win$ $(m/s^{2})$')
plt.xlabel('Time ' + r'$(sec)$', fontsize=12)
plt.ylabel('Parameter '+ r'$(R_win)$', fontsize=12)
plt.title('Building Parameter - NLP Solution '+ r'$R_win$', fontsize=14)
plt.legend(loc='upper right')
plt.tight_layout()
plt.grid(True)


# Plotting  Parameters - C_in -  of Nonlinear System
plt.subplot(211)
plt.plot(time_vector, C_in_sol*np.ones((np.shape(time_vector)[0],1)), label=r'$C_in$ $(m/s^{2})$')
plt.xlabel('Time ' + r'$(sec)$', fontsize=12)
plt.ylabel('Parameter '+ r'$(C_in)$', fontsize=12)
plt.title('Building Parameter - NLP Solution '+ r'$C_in$', fontsize=14)
plt.legend(loc='upper right')
plt.tight_layout()
plt.grid(True)


# Plotting  Parameters - C1 -  of Nonlinear System
plt.subplot(211)
plt.plot(time_vector, C1_sol*np.ones((np.shape(time_vector)[0],1)), label=r'$C1$ $(m/s^{2})$')
plt.xlabel('Time ' + r'$(sec)$', fontsize=12)
plt.ylabel('Parameter '+ r'$(C1)$', fontsize=12)
plt.title('Building Parameter - NLP Solution '+ r'$C1$', fontsize=14)
plt.legend(loc='upper right')
plt.tight_layout()
plt.grid(True)

# Plotting  Parameters - C2 -  of Nonlinear System
plt.subplot(211)
plt.plot(time_vector, C2_sol*np.ones((np.shape(time_vector)[0],1)), label=r'$C2$ $(m/s^{2})$')
plt.xlabel('Time ' + r'$(sec)$', fontsize=12)
plt.ylabel('Parameter '+ r'$(C2)$', fontsize=12)
plt.title('Building Parameter - NLP Solution '+ r'$C2$', fontsize=14)
plt.legend(loc='upper right')
plt.tight_layout()
plt.grid(True)

# Plotting  Parameters - C3 -  of Nonlinear System
plt.subplot(211)
plt.plot(time_vector, C3_sol*np.ones((np.shape(time_vector)[0],1)), label=r'$C3$ $(m/s^{2})$')
plt.xlabel('Time ' + r'$(sec)$', fontsize=12)
plt.ylabel('Parameter '+ r'$(C3)$', fontsize=12)
plt.title('Building Parameter - NLP Solution '+ r'$C3$', fontsize=14)
plt.legend(loc='upper right')
plt.tight_layout()
plt.grid(True)



# Plotting Figures
plt.figure()

# Plotting  Variables - v -  of Nonlinear System
plt.subplot(311)
plt.plot(time_vector, v_sol[0:-1].transpose(), label=r'$v$ $(rads/s)$')
plt.xlabel('Time ' + r'$(sec)$', fontsize=12)
plt.ylabel('Variable '+ r'$(v)$', fontsize=12)
plt.title('Building Variable - NLP Solution '+ r'$v$', fontsize=14)
plt.legend(loc='upper right')
plt.tight_layout()
plt.grid(True)

# Plotting  Variables - w_T_ave -  of Nonlinear System
plt.subplot(312)
plt.plot(time_vector, w_T_ave_sol, label=r'$w_{T_{ave}}$ $(rads)$')
plt.xlabel('Time ' + r'$(sec)$', fontsize=12)
plt.ylabel('Variable '+ r'$(w_{T_{ave}})$', fontsize=12)
plt.title('Building Variable - NLP Solution '+ r'$w_{T_{ave}}$', fontsize=14)
plt.legend(loc='upper right')
plt.tight_layout()
plt.grid(True)
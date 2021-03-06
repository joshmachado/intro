from astropy.table import Table
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import pandas as pd
import os.path

sources = ['ngc3621', 'ngc6300']
loc = '/Users/josh/projects/intro/'
res = np.array([60, 90, 120, 150])
mean_dist = np.zeros([4,3])
mean_beam_sep = np.zeros([4,3])
percentiles = np.zeros([4,15]) #5th, 16th, 50th, 84th, 95th
perc = [5,16,50,84,95]
for i in range(len(res)):
    for z in range(len(sources)):
        fp = '/Users/josh/projects/intro/'+sources[z]+'/max/'+sources[z]+'_12m+7m+tp_co21_'+str(res[i])+'pc_props.fits.bz2'
        if os.path.isfile(fp) == True:
            tab = Table.read(fp)
            cloudnum = np.array(tab['CLOUDNUM'])
            distance = np.array(tab['DISTANCE_PC'])
            x = np.array(tab['XMAX_DEG'])
            y = np.array(tab['YMAX_DEG'])
            xs = (x-np.mean(x))*np.cos(np.deg2rad(y)) #correction RA = RAcos(Dec)
            dist = np.zeros((len(x),len(x)))
            nn = np.zeros(len(x)) #stores CloudNum of nearest neighbor
            mindist = np.zeros(len(x)) #stores distance to nearest neighbor
            nn2 = np.zeros(len(x)) #stores CloudNum of 2nd nearest neighbor
            mindist2 = np.zeros(len(x)) #stores distance to 2nd nearest neighbor
            nn3 = np.zeros(len(x)) #stores CloudNum of 3rd nearest neighbor
            mindist3 = np.zeros(len(x)) #stores distance to 3rd nearest neighbor
            k = 0
            j = 0
            while k < len(x):
                for j in range(len(x)):
                    dist[k,j] = np.sqrt(np.square(xs[k] - xs[j]) + np.square(y[k] - y[j]))
                k+=1
            dist[dist == 0] = np.nan
            for k in range(len(x)):
                ind = np.where(dist[k] == np.nanmin(dist[k])) #index of nearest neighbor
                ind2 = np.where(dist[k] == np.partition(dist[k], 1)[1]) #index of 2nd nearest neighbor
                ind3 = np.where(dist[k] == np.partition(dist[k], 2)[2]) #index of 3rd nearest neighbor
                mindist[k] = np.deg2rad(dist[k,int(ind[0])])*distance[0]
                nn[k] = int(ind[0])+1
                if len(ind2[0]) == 1:
                    mindist2[k] = np.deg2rad(dist[k,int(ind2[0])])*distance[0]
                    nn2[k] = int(ind2[0])+1
                else:
                    mindist2[k] = np.deg2rad(dist[k,int(ind2[0][0])])*distance[0]
                    nn2[k] = int(ind2[0][1])+1
                if len(ind3[0]) == 1:
                    mindist3[k] = np.deg2rad(dist[k,int(ind3[0])])*distance[0]
                    nn3[k] = int(ind3[0])+1
                else:
                    mindist3[k] = np.deg2rad(dist[k,int(ind3[0][0])])*distance[0]
                    nn3[k] = int(ind3[0][1])+1


            ### LETS GATHER SOME STATS ###
            mean_dist[i] = [np.mean(mindist), np.mean(mindist2), np.mean(mindist3)]
            mean_cloud_sep = [mindist, mindist2, mindist3]/np.nanmean(tab['RAD_PC'])
            beam_sep = [mindist, mindist2, mindist3]/tab['BEAMFWHM_PC'][0]
            percentiles[i] = [np.percentile(mindist, 5), np.percentile(mindist2, 5), np.percentile(mindist3, 5),
            np.percentile(mindist, 16), np.percentile(mindist2, 16), np.percentile(mindist3, 16),
            np.percentile(mindist, 50), np.percentile(mindist2, 50), np.percentile(mindist3, 50),
            np.percentile(mindist, 84), np.percentile(mindist2, 84), np.percentile(mindist3, 84),
            np.percentile(mindist, 95), np.percentile(mindist2, 95), np.percentile(mindist3, 95)] ##Go back and make this a loop
            mean_beam_sep[i] = [np.mean(mindist), np.mean(mindist2), np.mean(mindist3)]/tab['BEAMFWHM_PC'][0]


            ### Compile info into dataframe ###
            cat = pd.DataFrame({'cloudnum':cloudnum, 'x':x, 'corr_x':xs, 'y':y,
            'nn_index':nn,  'nn2_index':nn2, 'nn3_index':nn3,
            'min_dist':mindist, 'min_dist2nd':mindist2, 'min_dist3rd':mindist3,
            'mean_cloud_sep_nn':mean_cloud_sep[0], 'mean_cloud_sep_nn2':mean_cloud_sep[1], 'mean_cloud_sep_nn3':mean_cloud_sep[2],
            'beam_sep_nn':beam_sep[0], 'beam_sep_nn2':beam_sep[1], 'beam_sep_nn3':beam_sep[2]})
            cat.to_csv(loc+'/'+sources[z]+'/max/'+sources[z]+'_'+str(res[i])+'pc_cloud_stats.csv', index=False)
            print(str(sources[z])+' '+str(res[i])+'pc done')
        else:
            print(str(sources[z])+' '+str(res[i])+'pc not found')
print('Gathering stats...')

#peak_stats = pd.DataFrame({'res_pc':res,
#'mean_dist_nn':mean_dist[:,0], 'mean_dist_nn2':mean_dist[:,1], 'mean_dist_nn3':mean_dist[:,2],
#'5th_nn':percentiles[:,0], '5th_nn2':percentiles[:,1], '5th_nn3':percentiles[:,2],
#'16th_nn':percentiles[:,3], '16th_nn2':percentiles[:,4], '16th_nn3':percentiles[:,5],
#'50th_nn':percentiles[:,6], '50th_nn2':percentiles[:,7], '50th_nn3':percentiles[:,8],
#'84th_nn':percentiles[:,9], '84th_nn2':percentiles[:,10], '84th_nn3':percentiles[:,11],
#'95th_nn':percentiles[:,12], '95th_nn2':percentiles[:,13], '95th_nn3':percentiles[:,14],
#'mean_beam_sep':mean_beam_sep[:,0],'mean_beam_sep2':mean_beam_sep[:,1], 'mean_beam_sep3':mean_beam_sep[:,2]})

#peak_stats.to_csv(loc+'/'+source+'/max/'+source+'_stats.csv', index=False)

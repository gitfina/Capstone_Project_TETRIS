import streamlit as st
import altair as alt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from numerize import numerize
from adjustText import adjust_text
import geopandas as gpd

# Configure
st.set_page_config(
    page_title="Capstone Project Dashboard",
    layout="centered", page_icon="📈",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
st.title('Pengaruh Pemberian Kredit Sebagai Pemicu Pertumbuhan Produk Regional Domestik Bruto')

# Import dataframe
kp = pd.read_csv('https://raw.githubusercontent.com/Fery-K/Capstone_Project_TETRIS/master/Datasets/kredit_provinsi.csv')
k_mk = pd.read_csv('https://raw.githubusercontent.com/Fery-K/Capstone_Project_TETRIS/master/Datasets/kredit_modal_kerja_bank.csv')
k_i = pd.read_csv('https://raw.githubusercontent.com/Fery-K/Capstone_Project_TETRIS/master/Datasets/kredit_investasi_bank.csv')
k_k = pd.read_csv('https://raw.githubusercontent.com/Fery-K/Capstone_Project_TETRIS/master/Datasets/kredit_konsumsi_bank.csv')
pdrb = pd.read_csv('https://raw.githubusercontent.com/Fery-K/Capstone_Project_TETRIS/master/Datasets/pdrb.csv')

# Impute missing value
pdrb.loc[33, 'tahun_2011'], pdrb.loc[33, 'tahun_2012'] = 0, 0

# Data Prep

# Data Kredit Berdasarkan Provinsi
kp_pivot = kp.pivot(index='provinsi', columns='tahun', values='kredit').reset_index()

# Data Kredit Berdasarkan Jenis Penggunaan
k_k_tahun = k_k.groupby('tahun').sum()
k_i_tahun = k_i.groupby('tahun').sum()
k_mk_tahun = k_mk.groupby('tahun').sum()
k_k_tahun['jenis'] = ['konsumsi' for i in range(k_k_tahun.shape[0])]
k_i_tahun['jenis'] = ['investasi' for j in range(k_i_tahun.shape[0])]
k_mk_tahun['jenis'] = ['modal kerja' for k in range(k_mk_tahun.shape[0])]

k_jenis = pd.concat([k_k_tahun, k_i_tahun, k_mk_tahun]).reset_index()
k_pivot = k_jenis.pivot(index='tahun', columns='jenis', values='kredit').reset_index()

# Data PDRB Berdasarkan Provinsi
dg = gpd.read_file('https://github.com/Fery-K/Capstone_Project_TETRIS/raw/master/Provinsi%20Shapefiles/Batas%20Provinsi.shp')
pdrb['provinsi'] = pdrb['provinsi'].str.upper()
dg['Provinsi'] = dg['Provinsi'].replace(['KEPULAUAN BANGKA BELITUNG', 'DKI JAKARTA', 'DAERAH ISTIMEWA YOGYAKARTA'],
                                       ['BANGKA BELITUNG', 'D.K.I. JAKARTA', 'D.I. YOGYAKARTA'])
pdrb.columns = ['no', 'provinsi'] + [(2011+i) for i in range(12)]
dg_pdrb = pd.merge(dg, pdrb, left_on='Provinsi', right_on='provinsi')

# Data Hubungan Kredit dan PDRB
pdrb_ver = pd.melt(pdrb, id_vars=['no', 'provinsi'],
                   value_vars=[(2011+i) for i in range(12)],
                   var_name = 'tahun',
                   value_name = 'PDRB')
kp['provinsi'] = kp['provinsi'].str.upper()
kp_pdrb = pd.merge(kp[kp['tahun'] >= 2011].reset_index(),
                   pdrb_ver[pdrb_ver['provinsi'] != 'NASIONAL'],
                   on=['provinsi', 'tahun'])

pdrb_ver = pd.melt(pdrb, id_vars=['no', 'provinsi'],
                   value_vars=[(2011+i) for i in range(12)],
                   var_name='tahun',
                   value_name='PDRB')
k_pdrb = pd.merge(k_pivot[k_pivot['tahun'] >= 2011],
                  pdrb_ver.groupby('tahun')[['tahun', 'PDRB']].sum(),
                  on='tahun')

# Title and Prologue

# Header 1
st.header('Obsevasi Data Kredit dan PDRB')

tab1, tab2 = st.tabs(['Data Jumlah Pemberian Kredit',
                      'Data Pertumbuhan PDRB'])

with tab1:
    # Input By User
    iTahun_awal, iTahun_akhir = st.select_slider(
        'Pilih Tahun',
        options=[i for i in range(2002, 2023)],
        value=(2002, 2022),
        format_func=lambda x: f'Tahun {x}'
    )
    bydata1 = iTahun_awal
    bydata2 = iTahun_akhir

    # Plotting
    fig, ax = plt.subplots(figsize=(4, 5))
    kp_pivot.plot(
        x='provinsi',
        y=kp_pivot.loc[:, bydata1:bydata2].columns,
        kind='barh',
        stacked=True,
        colormap='tab20c',
        ax=ax)

    # Plot Setting
    ax.set_title('Jumlah Rata-Rata Kredit per Tahun Tiap Provinsi', fontsize=6)
    ax.set_xlabel('Jumlah Kredit (Milyar Rupiah)', fontsize=6)
    ax.set_ylabel('')
    ax.set_xscale('log')
    ax.legend(prop={'size': 3})
    ax.tick_params(axis='x', labelsize=5)
    ax.tick_params(axis='y', labelsize=5)

    st.pyplot(fig)

    # Horizontal Divider
    st.divider()

    # Subheader 1

    # Input By User
    st.text('Jenis Penggunaan Kredit')
    col1, col2, col3 = st.columns(3)

    with col1:
        iKonsumsi = st.checkbox('konsumsi', True)
    with col2:
        iInvestasi = st.checkbox('investasi', True)
    with col3:
        iModalKerja = st.checkbox('modal kerja', True)

    bydata = []

    if iKonsumsi:
        bydata.append('konsumsi')
    else:
        if 'konsumsi' in bydata:
            bydata.remove('konsumsi')

    if iInvestasi:
        bydata.append('investasi')
    else:
        if 'investasi' in bydata:
            bydata.remove('investasi')

    if iModalKerja:
        bydata.append('modal kerja')
    else:
        if 'modal kerja' in bydata:
            bydata.remove('modal kerja')

    # Plotting
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    k_pivot[['tahun'] + bydata].plot(x='tahun',
                                     kind='bar',
                                     stacked=True,
                                     colormap='tab20c',
                                     ax=ax2)

    # Plot Setting
    x_ax = [0.5 * i * (10 ** 6) for i in range(1, 11)]
    plt.title('Jumlah Rata-Rata Kredit per Tahun Berdasarkan Jenis Penggunaan')
    plt.xticks(rotation=0)
    plt.yticks(x_ax, [numerize.numerize(n) for n in x_ax])
    plt.ylabel('Jumlah Kredit (Milyar Rupiah)')
    plt.xlabel('Tahun')

    st.pyplot(fig2)

with tab2:
    # Berdasarkan Tahun ke Tahun
    iTahun1, iTahun2 = st.select_slider(
        'Pilih Tahun',
        options=[i for i in range(2011, 2023)],
        value=(2011, 2022),
        format_func=lambda x: f'Tahun {x}'
    )
    bydata3 = iTahun1
    bydata4 = iTahun2

    col_a, col_b = st.columns(2)

    with col_a:
        # Plotting
        fig3, ax3 = plt.subplots(figsize=(12, 6))
        dg_pdrb.plot(column=bydata3,
                     cmap='summer_r',
                     legend=True, legend_kwds={'shrink': 0.6},
                     ax=ax3)

        # Plot Setting
        highest1 = dg_pdrb[dg_pdrb[bydata3] == dg_pdrb[bydata3].max()]
        lowest1 = dg_pdrb[dg_pdrb[bydata3] == dg_pdrb[bydata3].min()]
        highest_prov1 = dg_pdrb[dg_pdrb[bydata3] == dg_pdrb[bydata3].max()]['provinsi'].values[0]
        lowest_prov1 = dg_pdrb[dg_pdrb[bydata3] == dg_pdrb[bydata3].min()]['provinsi'].values[0]

        highest_text1 = ax3.annotate(f'Highest: {highest_prov1}',
                                     xy=(highest1.geometry.centroid.x, highest1.geometry.centroid.y),
                                     xytext=(highest1.geometry.centroid.x + 1, highest1.geometry.centroid.y + 2),
                                     ha='center', arrowprops=dict(facecolor='black', arrowstyle="->"))

        lowest_text1 = ax3.annotate(f'Lowest: {lowest_prov1}',
                                    xy=(lowest1.geometry.centroid.x, lowest1.geometry.centroid.y),
                                    xytext=(lowest1.geometry.centroid.x + 1, lowest1.geometry.centroid.y + 2),
                                    ha='center', arrowprops=dict(facecolor='black', arrowstyle="->"))

        plt.title('Persebaran Pertumbuhan PDRB Tiap Provinsi')
        plt.xticks([])
        plt.yticks([])
        plt.ylabel(f'Pertumbuhan PDRB Tahun {bydata3}', labelpad=-565)

        st.pyplot(fig3)

    with col_b:
        # Plotting
        fig4, ax4 = plt.subplots(figsize=(12, 6))
        dg_pdrb.plot(column=bydata4,
                     cmap='summer_r',
                     legend=True, legend_kwds={'shrink': 0.6},
                     ax=ax4)

        # Plot Setting
        highest2 = dg_pdrb[dg_pdrb[bydata4] == dg_pdrb[bydata4].max()]
        lowest2 = dg_pdrb[dg_pdrb[bydata4] == dg_pdrb[bydata4].min()]
        highest_prov2 = dg_pdrb[dg_pdrb[bydata4] == dg_pdrb[bydata4].max()]['provinsi'].values[0]
        lowest_prov2 = dg_pdrb[dg_pdrb[bydata4] == dg_pdrb[bydata4].min()]['provinsi'].values[0]

        highest_text2 = ax4.annotate(f'Highest: {highest_prov2}',
                                     xy=(highest2.geometry.centroid.x, highest2.geometry.centroid.y),
                                     xytext=(highest2.geometry.centroid.x + 1, highest2.geometry.centroid.y + 2),
                                     ha='center', arrowprops=dict(facecolor='black', arrowstyle="->"))

        lowest_text2 = ax4.annotate(f'Lowest: {lowest_prov2}',
                                    xy=(lowest2.geometry.centroid.x, lowest2.geometry.centroid.y),
                                    xytext=(lowest2.geometry.centroid.x + 1, lowest2.geometry.centroid.y + 2),
                                    ha='center', arrowprops=dict(facecolor='black', arrowstyle="->"))

        plt.title('Persebaran Pertumbuhan PDRB Tiap Provinsi')
        plt.xticks([])
        plt.yticks([])
        plt.ylabel(f'Pertumbuhan PDRB Tahun {bydata4}', labelpad=-565)

        st.pyplot(fig4)

    # Horizontal Divider
    st.divider()

    # Secara Keseluruhan Tahun 2011-2022
    iAgg_method = st.selectbox('Agregasi Berdasarkan',
                               ['Jumlah', 'Rata-Rata', 'Median', 'Maksimum', 'Kuartil 1', 'Kuartil 3'])
    bydata = 'Agg'
    if iAgg_method == 'Jumlah':
        agg_method = sum
    elif iAgg_method == 'Rata-Rata':
        agg_method = lambda x: x.mean()
    elif iAgg_method == 'Median':
        agg_method = lambda x: x.mean()
    elif iAgg_method == 'Maksimum':
        agg_method = max
    elif iAgg_method == 'Kuartil 1':
        agg_method = lambda x: x.quantile(0.25)
    else:
        agg_method = lambda x: x.quantile(0.75)

    dg_pdrb['Agg'] = dg_pdrb[[i for i in range(2011, 2023)]].apply(agg_method, axis=1)

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 6))
    dg_pdrb.plot(column=bydata,
                 cmap='summer_r',
                 legend=True, legend_kwds={'shrink': 0.6},
                 ax=ax)

    # Plot Setting
    highest = dg_pdrb[dg_pdrb[bydata] == dg_pdrb[bydata].max()]
    lowest = dg_pdrb[dg_pdrb[bydata] == dg_pdrb[bydata].min()]
    highest_prov = dg_pdrb[dg_pdrb[bydata] == dg_pdrb[bydata].max()]['provinsi'].values[0]
    lowest_prov = dg_pdrb[dg_pdrb[bydata] == dg_pdrb[bydata].min()]['provinsi'].values[0]

    highest_text = ax.annotate(f'Highest: {highest_prov}',
                               xy=(highest.geometry.centroid.x, highest.geometry.centroid.y),
                               xytext=(highest.geometry.centroid.x + 1, highest.geometry.centroid.y + 2),
                               ha='center', arrowprops=dict(facecolor='black', arrowstyle="->"))

    lowest_text = ax.annotate(f'Lowest: {lowest_prov}', xy=(lowest.geometry.centroid.x, lowest.geometry.centroid.y),
                              xytext=(lowest.geometry.centroid.x + 1, lowest.geometry.centroid.y + 2),
                              ha='center', arrowprops=dict(facecolor='black', arrowstyle="->"))

    plt.title('Persebaran Pertumbuhan PDRB Tiap Provinsi')
    plt.xticks([])
    plt.yticks([])
    plt.ylabel(f'Pertumbuhan PDRB Agregasi {iAgg_method}', labelpad=-565)

    st.pyplot(fig)


# Header 2
st.header('Hubungan Pemberian Kredit dan Pertumbuhan PDRB')

tab_a, tab_b = st.tabs(['Berdasarkan Provinsi',
                         'Berdasarkan Jenis Penggunaan'])

with tab_a:
    # Secara Keseluruhan Provinsi
    df = kp_pdrb.groupby('provinsi')[['provinsi', 'kredit', 'PDRB']].mean().reset_index()

    # Plotting
    plot2 = plt.figure(figsize=(12, 6))
    sns.regplot(data=df,
                x='kredit', y='PDRB',
                line_kws={'color': 'lightblue', 'label': 'IDEAL'})

    # Plot Setting
    plt.title('Hubungan Posisi Kredit Dengan PDRB Tahun 2011-2022 Berdasarkan Lokasi')
    plt.xlabel('Rata-Rata Kredit')
    plt.legend(loc='best')

    prov = ['KALIMANTAN TIMUR', 'KEPULAUAN RIAU', 'RIAU', 'KALIMANTAN UTARA', 'PAPUA BARAT',
            'JAWA BARAT', 'JAWA TIMUR', 'JAWA TENGAH']
    for p in prov:
        plt.text(df[df['provinsi'] == p]['kredit'],
                 df[df['provinsi'] == p]['PDRB'],
                 p, ha='left', va='bottom')

    st.pyplot(plot2)

    # Horizontal Divider
    st.divider()

    # Berdasarkan Provinsi
    prov = st.selectbox('Pilih Provinsi',
                        ['ACEH', 'SUMATERA UTARA', 'SUMATERA BARAT', 'RIAU', 'JAMBI',
                         'SUMATERA SELATAN', 'BANGKA BELITUNG', 'BENGKULU', 'LAMPUNG',
                         'BANTEN', 'D.K.I. JAKARTA', 'JAWA BARAT', 'JAWA TENGAH',
                         'D.I. YOGYAKARTA', 'JAWA TIMUR', 'BALI', 'NUSA TENGGARA BARAT',
                         'NUSA TENGGARA TIMUR', 'KALIMANTAN BARAT', 'KALIMANTAN TENGAH',
                         'KALIMANTAN SELATAN', 'KALIMANTAN TIMUR', 'SULAWESI UTARA',
                         'GORONTALO', 'SULAWESI TENGAH', 'SULAWESI SELATAN',
                         'SULAWESI TENGGARA', 'MALUKU UTARA', 'MALUKU', 'PAPUA',
                         'PAPUA BARAT', 'SULAWESI BARAT', 'KEPULAUAN RIAU',
                         'KALIMANTAN UTARA']
                        )
    df = kp_pdrb[kp_pdrb['provinsi'] == prov]

    # Plotting
    plot1 = plt.figure(figsize=(12, 6))
    sns.regplot(data=df,
                x='kredit', y='PDRB',
                line_kws={'color': 'lightblue', 'label': prov})
    corr = df['kredit'].corr(kp_pdrb['PDRB'])

    # Plot Setting
    plt.title('Hubungan Posisi Kredit Dengan PDRB Tahun 2011-2022 Berdasarkan Lokasi')
    plt.xlabel('Kredit')
    plt.legend(loc='best')
    plt.annotate(f'Correlation: {corr:.4f}', xy=(0.01, 0.9), xycoords='axes fraction')

    txt = [plt.text(df['kredit'].values[0],
                    df['PDRB'].values[0],
                    df['tahun'].values[0],
                    ha='left', va='bottom')]

    for i in range(len(df) - 1):
        if (df['PDRB'].values[i] > df['PDRB'].values[i + 1]) | (
                df['kredit'].values[i] > df['kredit'].values[i + 1]):
            txt.append(plt.text(df['kredit'].values[i + 1],
                                df['PDRB'].values[i + 1],
                                df['tahun'].values[i + 1],
                                ha='left', va='bottom', color='crimson'))
        else:
            txt.append(plt.text(df['kredit'].values[i + 1],
                                df['PDRB'].values[i + 1],
                                df['tahun'].values[i + 1],
                                ha='left', va='bottom'))
    adjust_text(txt)

    st.pyplot(plot1)


with tab_b:
    # Berdasarkan Jenis Penggunaan
    jenis_kredit = st.radio('Pilih Jenis Penggunaan Kredit',
                            ['konsumsi', 'investasi', 'modal kerja'])
    # Plotting
    plot3 = plt.figure(figsize=(12, 6))
    sns.regplot(data=k_pdrb,
                x=jenis_kredit,
                y='PDRB',
                line_kws={'color': 'lightblue', 'label': jenis_kredit})
    corr = k_pdrb[jenis_kredit].corr(k_pdrb['PDRB'])

    # Plot Setting
    plt.title('Hubungan Posisi Kredit Dengan PDRB Tahun 2011-2022 Berdasarkan Jenis Penggunaan')
    plt.xlabel(f'Kredit {jenis_kredit}')
    plt.legend(loc='upper left')
    plt.annotate(f'Correlation: {corr:.4f}', xy=(0.01, 0.9), xycoords='axes fraction')

    txt = [plt.text(k_pdrb[jenis_kredit][0], k_pdrb['PDRB'][0], k_pdrb['tahun'][0], ha='left', va='bottom')]
    for i in range(len(k_pdrb) - 1):
        if (k_pdrb['PDRB'][i] > k_pdrb['PDRB'][i + 1]) | (k_pdrb[jenis_kredit][i] > k_pdrb[jenis_kredit][i + 1]):
            txt.append(plt.text(k_pdrb[jenis_kredit][i + 1],
                                k_pdrb['PDRB'][i + 1],
                                k_pdrb['tahun'][i + 1],
                                ha='left', va='bottom', color='crimson'))
        else:
            txt.append(plt.text(k_pdrb[jenis_kredit][i + 1],
                                k_pdrb['PDRB'][i + 1],
                                k_pdrb['tahun'][i + 1],
                                ha='left', va='bottom'))
    adjust_text(txt)

    st.pyplot(plot3)

    # Horizontal Divider
    st.divider()

    # Secara Keseluruhan Penggunaan
    iAgg_method2 = st.selectbox('Agregasi Berdasarkan',
                               ['Jumlah', 'Rata-Rata', 'Median', 'Kuartil 1', 'Kuartil 3'])
    if iAgg_method2 == 'Jumlah':
        agg_method2 = sum
    elif iAgg_method2 == 'Rata-Rata':
        agg_method2 = lambda x: x.mean()
    elif iAgg_method2 == 'Median':
        agg_method2 = lambda x: x.mean()
    elif iAgg_method2 == 'Kuartil 1':
        agg_method2 = lambda x: x.quantile(0.25)
    else:
        agg_method2 = lambda x: x.quantile(0.75)

    k_pdrb['Agg'] = k_pdrb[['investasi', 'konsumsi', 'modal kerja']].apply(agg_method2, axis=1)

    # Plotting
    plot4 = plt.figure(figsize=(12, 6))
    sns.regplot(data=k_pdrb,
                x='Agg',
                y='PDRB',
                line_kws={'color': 'lightblue', 'label': f'Agregasi {iAgg_method2}'})
    corr = k_pdrb['Agg'].corr(k_pdrb['PDRB'])

    # Plot Setting
    plt.title('Hubungan Posisi Kredit Dengan PDRB Tahun 2011-2022 Berdasarkan Jenis Penggunaan')
    plt.xlabel(f'Kredit Agregasi')
    plt.legend(loc='upper left')
    plt.annotate(f'Correlation: {corr:.4f}', xy=(0.01, 0.9), xycoords='axes fraction')

    txt = [plt.text(k_pdrb['Agg'][0], k_pdrb['PDRB'][0], k_pdrb['tahun'][0], ha='left', va='bottom')]
    for i in range(len(k_pdrb) - 1):
        if (k_pdrb['PDRB'][i] > k_pdrb['PDRB'][i + 1]) | (k_pdrb['Agg'][i] > k_pdrb['Agg'][i + 1]):
            txt.append(plt.text(k_pdrb['Agg'][i + 1],
                                k_pdrb['PDRB'][i + 1],
                                k_pdrb['tahun'][i + 1],
                                ha='left', va='bottom', color='crimson'))
        else:
            txt.append(plt.text(k_pdrb['Agg'][i + 1],
                                k_pdrb['PDRB'][i + 1],
                                k_pdrb['tahun'][i + 1],
                                ha='left', va='bottom'))
    adjust_text(txt)
    st.pyplot(plot4)
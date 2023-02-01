import cdstoolbox as ct

layout = {
    'output_align': 'bottom'
}

extent = {
    'Europe': [-11, 35, 34, 60],
    'Arctic': [-180, 180, 70, 90],
    'Mediterranean': [-6, 34, 31, 45],
    'Global': [-180, 180, -90, 90]
}

@ct.application(title='Calculate trends', layout=layout)
@ct.input.dropdown('region', label='Region', values=['Europe', 'Arctic', 'Mediterranean', 'Global'],
                   description='Map will change accordingly.')
@ct.output.figure()
@ct.output.figure()
def trend_app(region):
    """
    Application main steps:

    - retrieve a variable over a defined time range
    - compute the monthly mean
    - select a region
    - compute the linear trend in time for each gridpoint in that region
    - plot trends and their standard errors on two separate maps
    """

    data = ct.catalogue.retrieve(
        'reanalysis-era5-single-levels',
        {
            'variable': '2m_temperature',
            'grid': ['3', '3'],
            'product_type': 'reanalysis',
            'year': [
                '2008', '2009', '2010',
                '2011', '2012', '2013',
                '2014', '2015', '2016',
                '2017'
            ],
            'month': [
                '01', '02', '03', '04', '05', '06',
                '07', '08', '09', '10', '11', '12'
            ],
            'day': [
                '01', '02', '03', '04', '05', '06',
                '07', '08', '09', '10', '11', '12',
                '13', '14', '15', '16', '17', '18',
                '19', '20', '21', '22', '23', '24',
                '25', '26', '27', '28', '29', '30',
                '31'
            ],
            'time': ['00:00', '06:00', '12:00', '18:00'],
        }
    )

    data_mean = ct.climate.monthly_mean(data)
    data_select = ct.cube.select(data_mean, extent=extent[region])

    a, b, a_std, b_std = ct.stats.trend(
        data_select, slope_units='K year-1')

    projection = ct.cdsplot.crs.NorthPolarStereo() if region == 'Arctic' else \
        ct.cdsplot.crs.PlateCarree()
    fig_b = ct.cdsplot.geomap(
        b, projection=projection, pcolormesh_kwargs={'cmap': 'coolwarm'},
        title='Near Surface Air Temperature Trend'
    )

    fig_std = ct.cdsplot.geomap(
        b_std, projection=projection, pcolormesh_kwargs={'cmap': 'coolwarm'},
        title='Near Surface Air Temperature Trend\nStandard deviation'
    )

    return fig_b, fig_std


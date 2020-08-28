import java.io.*;

public class trackevent_tester
{
	public static void main(String argv[])
	{
		int i = -1, j = -1;

		/*
		double lt[][] = new double[][]
		{
			{65.6049, 5},
			{63.4114, 10},
			{63.6003, 15},
			{60.8030, 20},
			{66.4003, 25},
			{65.8027, 30},
			{66.8506, 35},
			{59.2030, 40},
			{56.4004, 45},
			{54.8179, 50},
			{54.4059, 55},
			{59.2030, 60},
			{64.2028, 65},
			{59.0339, 70},
			{55.0000, 75},
			{53.2635, 80},
			{50.6063, 85},
			{52.6308, 90},
			{51.4004, 95},
			{48.2701, 100},
			{51.4004, 105},
			{49.0408, 110},
			{49.0408, 115},
			{55.0000, 120},
			{56.4004, 125},
			{50.4480, 130},
			{47.8017, 135},
			{52.0096, 140},
			{50.4480, 145},
			{46.8615, 150}
		};
		//*/

		//*
		double lt[][] = new double[][]
		{
			{9.39, 4.00},
			{9.15, 8.00},
			{9.09, 12.00},
			{8.97, 16.00},
			{8.15, 20.00},
			{7.65, 24.00},
			{7.58, 28.00},
			{8.04, 32.00},
			{8.09, 36.00},
			{8.45, 40.00},
			{8.44, 44.00},
			{8.62, 48.00},
			{8.74, 52.00},
			{8.85, 56.00},
			{9.04, 60.00},
			{8.80, 64.00},
			{8.97, 68.00},
			{8.97, 72.00},
			{9.40, 76.00},
			{9.88, 80.00},
			{9.88, 84.00},
			{10.00, 88.00},
			{10.30, 92.00},
			{10.12, 96.00},
			{10.49, 100.00},
			{10.37, 104.00},
			{10.30, 108.00},
			{10.42, 112.00},
			{8.44, 116.00},
			{6.55, 120.00},
			{4.14, 124.00}
		};
		//*/

		int size = lt.length;

		/*
		int size = 4;
		
		double lengths[] = new double[size];
		double times[] = new double[size];

		for (j = 0; j < size; j++)
		{
			lengths[j] = Math.random() * 10.0;
			times[j] = 4.0 * (j + 1);
		}

		double lt[][] = new double[size][2];

		for (j = 0; j < size; j++)
		{
			lt[j][0] = lengths[j];
			lt[j][1] = times[j];
		}
		//*/

		double params[] = new double[]{Constants.SIMPLE_GROWTH_RATE, Constants.SIMPLE_GROWTH_LENGTH, Constants.COMPLEX_GROWTH_RATE, Constants.COMPLEX_GROWTH_LENGTH, Constants.SIMPLE_SHORTENING_RATE, Constants.SIMPLE_SHORTENING_LENGTH, Constants.COMPLEX_SHORTENING_RATE, Constants.COMPLEX_SHORTENING_LENGTH, Constants.SIMPLE_ATTENUATION_TIME, Constants.SIMPLE_ATTENUATION_LENGTH, Constants.COMPLEX_ATTENUATION_TIME, Constants.COMPLEX_ATTENUATION_LENGTH};

		TrackEvent te = new TrackEvent();

		te.choice = -2;

		te.start(lt, params);

		int events[][] = te.getEvents();

		/*
		for (j = 0; j < size; j++)
			System.out.printf("%.2f %.2f\n", lt[j][1], lt[j][0]);
		System.out.println();
		//*/

		for (j = 0; j < events.length; j++)
		{
			if (events[j][0] == 0)
				System.out.printf("# %c: ", 'G');
			else if (events[j][0] == 1)
				System.out.printf("# %c: ", 'S');
			else if (events[j][0] == 2)
				System.out.printf("# %c: ", 'A');
			else
				System.out.printf("# %c: ", 'E');

			System.out.printf("%.2f %.2f %.2f %.2f\n", lt[events[j][1]][1], lt[events[j][2]][1], lt[events[j][1]][0], lt[events[j][2]][0]);
		}
		System.out.println();

		for (j = 0; j < events.length; j++)
			System.out.printf("%.2f %.2f\n", lt[events[j][1]][1], lt[events[j][1]][0]);
		System.out.printf("%.2f %.2f\n", lt[events[j - 1][2]][1], lt[events[j - 1][2]][0]);
		System.out.println();
	}
}


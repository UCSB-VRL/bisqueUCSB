import java.io.*;
import java.util.*;

/*
 * Code for simple events:
 * SG   = G (Rate, Length)
 * SS   = S (Rate, Length)
 * SA   = A (Time, Length)
 * EGL  = F
 * EGR  = H
 * EGLR = H
 * ESL  = R
 * ESR  = T
 * ESLR = T
 *
 * Code for complex events:
 * g: (G|F|H|R|T)+ (Rate, Length)
 * s: (S|F|H|R|T)+ (Rate, Length)
 * a: (A|F|H|R|T)+ (Time, Rate, Length)
 * e: a
 * 
 */

public class TrackEvent
{
	public int size;
	public int c_size;
	public double params[];
	public double lengths[];
	public double times[];
	public double rates[];
	public char simple_events[];
	public Event events[];
	public Event c_events[];

	public double SIMPLE_GROWTH_RATE;
	public double SIMPLE_GROWTH_LENGTH;
	public double COMPLEX_GROWTH_RATE;
	public double COMPLEX_GROWTH_LENGTH;
	public double SIMPLE_SHORTENING_RATE;
	public double SIMPLE_SHORTENING_LENGTH;
	public double COMPLEX_SHORTENING_RATE;
	public double COMPLEX_SHORTENING_LENGTH;
	public double SIMPLE_ATTENUATION_TIME;
	public double SIMPLE_ATTENUATION_LENGTH;
	public double COMPLEX_ATTENUATION_TIME;
	public double COMPLEX_ATTENUATION_LENGTH;

	public int choice = 2;

	TrackEvent()
	{
	}

	public void start(double lentime[][], double pars[])
	{
		int i = -1, j = -1;

		size = lentime.length;

		//System.out.println(size);

		lengths = new double[size];
		times = new double[size];

		for (i = 0; i < size; i++)
		{
			lengths[i] = lentime[i][0];
			times[i] = lentime[i][1];
		}

		params = new double[pars.length];

		for (i = 0; i < params.length; i++)
			params[i] = pars[i];

		SIMPLE_GROWTH_RATE = params[0];
		SIMPLE_GROWTH_LENGTH = params[1];
		COMPLEX_GROWTH_RATE = params[2];
		COMPLEX_GROWTH_LENGTH = params[3];
		SIMPLE_SHORTENING_RATE = params[4];
		SIMPLE_SHORTENING_LENGTH = params[5];
		COMPLEX_SHORTENING_RATE = params[6];
		COMPLEX_SHORTENING_LENGTH = params[7];
		SIMPLE_ATTENUATION_TIME = params[8];
		SIMPLE_ATTENUATION_LENGTH = params[9];
		COMPLEX_ATTENUATION_TIME = params[10];
		COMPLEX_ATTENUATION_LENGTH = params[11];

		simple_events = new char[size - 1];

		c_size = size - 1;

		events = new Event[c_size];

		simple_track();

		track();
	}

	public void simple_track()
	{
		int i = -1;

		for (i = 0; i < size - 1; i++)
		{
			double delta_length = lengths[i + 1] - lengths[i];
			double delta_time = times[i + 1] - times[i];
			double delta_rate = delta_length * 60.0 / delta_time;

			if (delta_rate >= SIMPLE_GROWTH_RATE)
			{
				if (delta_length >= SIMPLE_GROWTH_LENGTH)
					simple_events[i] = 'G';
				else
					simple_events[i] = 'F';
			}
			else if (delta_rate <= SIMPLE_SHORTENING_RATE)
			{
				if (delta_length <= SIMPLE_SHORTENING_LENGTH)
					simple_events[i] = 'S';
				else
					simple_events[i] = 'R';
			}
			else
			{
				if ((delta_time >= SIMPLE_ATTENUATION_TIME) && (Math.abs(delta_length) <= SIMPLE_ATTENUATION_LENGTH))
					simple_events[i] = 'A';
				else
				{
					if (delta_rate >= 0)
					{
						if (delta_length >= SIMPLE_GROWTH_LENGTH)
							simple_events[i] = 'H';
						else
							simple_events[i] = 'H';
					}
					else // if (delta_rate < 0)
					{
						if (delta_length >= SIMPLE_SHORTENING_LENGTH)
							simple_events[i] = 'T';
						else
							simple_events[i] = 'T';
					}
				}
			}

			events[i] = new Event(simple_events[i], times[i], times[i + 1], i, i + 1);
			//events[i].printEvent();
		}

		//System.out.println();
	}

	public void track()
	{
		if (choice == 2)
			track2();
		else if (choice == 1)
			track1();
		//else
		//	track0();
	}

	public void track2()
	{
		int i = -1, j = -1, k = 0;

		c_events = new Event[size - 1];

		boolean undone = true;

		while (undone)
		{
			undone = false;

			k = 0;

			for (i = 0; i < c_size - 1; i++)
			{
				j = i + 1;
				while ((j < c_size) && (events[j].type == events[i].type))
					j++;

				c_events[k++] = new Event(events[i].type, events[i].start_time, events[j - 1].end_time, events[i].start_pos, events[j - 1].end_pos);
				//c_events[k - 1].printEvent();

				i = j - 1;
			}

			if (c_size > 1)
			{
				if (events[c_size - 1].type != events[c_size - 2].type)
				{
					i = c_size - 1;
					c_events[k++] = new Event(events[i].type, events[i].start_time, events[i].end_time, events[i].start_pos, events[i].end_pos);
					//c_events[k - 1].printEvent();
				}
			}
			else
			{
				c_events[k++] = new Event(events[0].type, events[0].start_time, events[0].end_time, events[0].start_pos, events[0].end_pos);
			}

			//System.out.println();

			c_size = k;

			for (i = 0; i < c_size; i++)
				events[i] = new Event(c_events[i]);

			k = 0;

			for (i = 0; i < c_size; i++)
			{
				if (isValid(events[i].type))
				{
					char none = events[i].type;

					double length = 0.0;
					double st = 0.0;
					double et = 0.0;
					double duration = 0.0;
					int sp = -1;
					int ep = -1;
					double rate = 0.0;

					if (none == 'G')
					{
						st = events[i].start_time;
						et = events[i].end_time;
						duration = et - st;
						sp = events[i].start_pos;
						ep = events[i].end_pos;
						length = lengths[ep] - lengths[sp];
						rate = length * 60.0 / duration;
						if (length < COMPLEX_GROWTH_LENGTH)
							events[i].type = 'F';
						if (rate < COMPLEX_GROWTH_RATE)
							events[i].type = 'H';
						events[i].printEvent();
					}

					if (none == 'S')
					{
						st = events[i].start_time;
						et = events[i].end_time;
						duration = et - st;
						sp = events[i].start_pos;
						ep = events[i].end_pos;
						length = lengths[ep] - lengths[sp];
						rate = length * 60.0 / duration;
						if (length > COMPLEX_SHORTENING_LENGTH)
							events[i].type = 'R';
						if (rate > COMPLEX_SHORTENING_RATE)
							events[i].type = 'T';
						events[i].printEvent();
					}

					if (none == 'A')
					{
						st = events[i].start_time;
						et = events[i].end_time;
						duration = et - st;
						sp = events[i].start_pos;
						ep = events[i].end_pos;
						length = attLength(sp, ep);
						rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
						boolean success = isAttenuation(length, duration, rate);
						if (!success)
						{
							if (rate >= 0.0)
								events[i].type = 'H';
							else
								events[i].type = 'T';
						}
						events[i].printEvent();
					}
				}
			}

			for (i = 0; i < c_size; i++)
			{
				if (!undone)
				{
					if (!isValid(events[i].type))
					{
						char left = 'E';
						char right = 'E';
						if (i != 0)
							left = events[i - 1].type;
						if (i != c_size - 1)
							right = events[i + 1].type;

						double length = 0.0;
						double st = 0.0;
						double et = 0.0;
						double duration = 0.0;
						int sp = -1;
						int ep = -1;
						double rate = 0.0;

						double stet[] = new double[2];
						int spep[] = new int[2];
						int index[] = new int[2];
						index[0] = i;
						index[1] = k;

						if (events[i].type == 'F')
						{
							if (left == right)
							{
								char both = left;
								if ((both == 'G') || (both == 'H'))
								{
									// try 'G' both
									if (tryGrowthBoth(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else if (both == 'A')
								{
									// try 'A' both
									if (tryAttenuationBoth(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
							}
							else
							{
								if ((left == 'G') || (left == 'H'))
								{
									// try 'G' left
									if (tryGrowthLeft(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
									if (right == 'A')
									{
										// try 'A' right
										if (tryAttenuationRight(index))
										{
											i = index[0];
											k = index[1];
											undone = true;
											continue;
										}
									}
									else
									{
										// try 'A' none
										if (tryAttenuationNone(index))
										{
											i = index[0];
											k = index[1];
											undone = true;
											continue;
										}
									}
								}
								else if ((right == 'G') || (right == 'H'))
								{
									// try 'G' right
									if (tryGrowthRight(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
									if (left == 'A')
									{
										// try 'A' left
										if (tryAttenuationLeft(index))
										{
											i = index[0];
											k = index[1];
											undone = true;
											continue;
										}
									}
									else
									{
										// try 'A' none
										if (tryAttenuationNone(index))
										{
											i = index[0];
											k = index[1];
											undone = true;
											continue;
										}
									}
								}
								else
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
							}
						}
						else if (events[i].type == 'H')
						{
							if (left == right)
							{
								char both = left;
								if ((both == 'G') || (both == 'F'))
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
									// try 'G' both
									if (tryGrowthBoth(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else if (both == 'A')
								{
									// try 'A' both
									if (tryAttenuationBoth(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
							}
							else
							{
								if (left == 'A')
								{
									// try 'A' left
									if (tryAttenuationLeft(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else if (right == 'A')
								{
									// try 'A' right
									if (tryAttenuationRight(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else if ((left == 'G') || (left == 'F'))
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
									// try 'G' left
									if (tryGrowthLeft(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else if ((right == 'G') || (right == 'F'))
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
									// try 'G' right
									if (tryGrowthRight(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
							}
						}
						else if (events[i].type == 'R')
						{
							if (left == right)
							{
								char both = left;
								if ((both == 'S') || (both == 'T'))
								{
									// try 'S' both
									if (tryShorteningBoth(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else if (both == 'A')
								{
									// try 'A' both
									if (tryAttenuationBoth(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
							}
							else
							{
								if ((left == 'S') || (left == 'T'))
								{
									// try 'S' left
									if (tryShorteningLeft(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
									if (right == 'A')
									{
										// try 'A' right
										if (tryAttenuationRight(index))
										{
											i = index[0];
											k = index[1];
											undone = true;
											continue;
										}
									}
									else
									{
										// try 'A' none
										if (tryAttenuationNone(index))
										{
											i = index[0];
											k = index[1];
											undone = true;
											continue;
										}
									}
								}
								else if ((right == 'S') || (right == 'T'))
								{
									// try 'S' right
									if (tryShorteningRight(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
									if (left == 'A')
									{
										// try 'A' left
										if (tryAttenuationLeft(index))
										{
											i = index[0];
											k = index[1];
											undone = true;
											continue;
										}
									}
									else
									{
										// try 'A' none
										if (tryAttenuationNone(index))
										{
											i = index[0];
											k = index[1];
											undone = true;
											continue;
										}
									}
								}
								else
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
							}
						}
						else if (events[i].type == 'T')
						{
							if (left == right)
							{
								char both = left;
								if ((both == 'S') || (both == 'R'))
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
									// try 'S' both
									if (tryShorteningBoth(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else if (both == 'A')
								{
									// try 'A' both
									if (tryAttenuationBoth(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
							}
							else
							{
								if (left == 'A')
								{
									// try 'A' left
									if (tryAttenuationLeft(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else if (right == 'A')
								{
									// try 'A' right
									if (tryAttenuationRight(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else if ((left == 'S') || (left == 'R'))
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
									// try 'S' left
									if (tryShorteningLeft(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else if ((right == 'S') || (right == 'R'))
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
									// try 'S' right
									if (tryShorteningRight(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
							}
						}
					}
				}

				c_events[k++] = new Event(events[i]);
				c_events[k - 1].printEvent();
			}

			//System.out.println();

			c_size = k;

			for (i = 0; i < c_size; i++)
				events[i] = new Event(c_events[i]);
		}
	}

	public void track1()
	{
		int i = -1, j = -1, k = 0;

		c_events = new Event[size - 1];

		boolean undone = true;

		while (undone)
		{
			undone = false;

			k = 0;

			for (i = 0; i < c_size - 1; i++)
			{
				j = i + 1;
				while ((j < c_size) && (events[j].type == events[i].type))
					j++;

				c_events[k++] = new Event(events[i].type, events[i].start_time, events[j - 1].end_time, events[i].start_pos, events[j - 1].end_pos);
				c_events[k - 1].printEvent();

				i = j - 1;
			}

			if (c_size > 1)
			{
				if (events[c_size - 1].type != events[c_size - 2].type)
				{
					i = c_size - 1;
					c_events[k++] = new Event(events[i].type, events[i].start_time, events[i].end_time, events[i].start_pos, events[i].end_pos);
					c_events[k - 1].printEvent();
				}
			}
			else
			{
				c_events[k++] = new Event(events[0].type, events[0].start_time, events[0].end_time, events[0].start_pos, events[0].end_pos);
			}

			//System.out.println();

			c_size = k;

			for (i = 0; i < c_size; i++)
				events[i] = new Event(c_events[i]);

			k = 0;

			for (i = 0; i < c_size; i++)
			{
				if (!isValid(events[i].type))
				{
					char left = 'E';
					char right = 'E';
					if (i != 0)
						left = events[i - 1].type;
					if (i != c_size - 1)
						right = events[i + 1].type;

					double length = 0.0;
					double st = 0.0;
					double et = 0.0;
					double duration = 0.0;
					int sp = -1;
					int ep = -1;
					double rate = 0.0;

					double stet[] = new double[2];
					int spep[] = new int[2];
					int index[] = new int[2];
					index[0] = i;
					index[1] = k;

					if (events[i].type == 'F')
					{
						if (left == right)
						{
							char both = left;
							if ((both == 'G') || (both == 'H'))
							{
								// try 'G' both
								if (tryGrowthBoth(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
								// try 'A' none
								if (tryAttenuationNone(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
							else if (both == 'A')
							{
								// try 'A' both
								if (tryAttenuationBoth(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
							else
							{
								// try 'A' none
								if (tryAttenuationNone(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
						}
						else
						{
							if ((left == 'G') || (left == 'H'))
							{
								// try 'G' left
								if (tryGrowthLeft(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
								if (right == 'A')
								{
									// try 'A' right
									if (tryAttenuationRight(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
							}
							else if ((right == 'G') || (right == 'H'))
							{
								// try 'G' right
								if (tryGrowthRight(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
								if (left == 'A')
								{
									// try 'A' left
									if (tryAttenuationLeft(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
							}
							else
							{
								// try 'A' none
								if (tryAttenuationNone(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
						}
					}
					else if (events[i].type == 'H')
					{
						if (left == right)
						{
							char both = left;
							if ((both == 'G') || (both == 'F'))
							{
								// try 'A' none
								if (tryAttenuationNone(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
								// try 'G' both
								if (tryGrowthBoth(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
							else if (both == 'A')
							{
								// try 'A' both
								if (tryAttenuationBoth(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
							else
							{
								// try 'A' none
								if (tryAttenuationNone(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
						}
						else
						{
							if (left == 'A')
							{
								// try 'A' left
								if (tryAttenuationLeft(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
							else if (right == 'A')
							{
								// try 'A' right
								if (tryAttenuationRight(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
							else if ((left == 'G') || (left == 'F'))
							{
								// try 'A' none
								if (tryAttenuationNone(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
								// try 'G' left
								if (tryGrowthLeft(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
							else if ((right == 'G') || (right == 'F'))
							{
								// try 'A' none
								if (tryAttenuationNone(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
								// try 'G' right
								if (tryGrowthRight(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
							else
							{
								// try 'A' none
								if (tryAttenuationNone(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
						}
					}
					else if (events[i].type == 'R')
					{
						if (left == right)
						{
							char both = left;
							if ((both == 'S') || (both == 'T'))
							{
								// try 'S' both
								if (tryShorteningBoth(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
								// try 'A' none
								if (tryAttenuationNone(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
							else if (both == 'A')
							{
								// try 'A' both
								if (tryAttenuationBoth(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
							else
							{
								// try 'A' none
								if (tryAttenuationNone(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
						}
						else
						{
							if ((left == 'S') || (left == 'T'))
							{
								// try 'S' left
								if (tryShorteningLeft(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
								if (right == 'A')
								{
									// try 'A' right
									if (tryAttenuationRight(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
							}
							else if ((right == 'S') || (right == 'T'))
							{
								// try 'S' right
								if (tryShorteningRight(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
								if (left == 'A')
								{
									// try 'A' left
									if (tryAttenuationLeft(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
								else
								{
									// try 'A' none
									if (tryAttenuationNone(index))
									{
										i = index[0];
										k = index[1];
										undone = true;
										continue;
									}
								}
							}
							else
							{
								// try 'A' none
								if (tryAttenuationNone(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
						}
					}
					else if (events[i].type == 'T')
					{
						if (left == right)
						{
							char both = left;
							if ((both == 'S') || (both == 'R'))
							{
								// try 'A' none
								if (tryAttenuationNone(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
								// try 'S' both
								if (tryShorteningBoth(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
							else if (both == 'A')
							{
								// try 'A' both
								if (tryAttenuationBoth(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
							else
							{
								// try 'A' none
								if (tryAttenuationNone(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
						}
						else
						{
							if (left == 'A')
							{
								// try 'A' left
								if (tryAttenuationLeft(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
							else if (right == 'A')
							{
								// try 'A' right
								if (tryAttenuationRight(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
							else if ((left == 'S') || (left == 'R'))
							{
								// try 'A' none
								if (tryAttenuationNone(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
								// try 'S' left
								if (tryShorteningLeft(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
							else if ((right == 'S') || (right == 'R'))
							{
								// try 'A' none
								if (tryAttenuationNone(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
								// try 'S' right
								if (tryShorteningRight(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
							else
							{
								// try 'A' none
								if (tryAttenuationNone(index))
								{
									i = index[0];
									k = index[1];
									undone = true;
									continue;
								}
							}
						}
					}
				}

				c_events[k++] = new Event(events[i]);
				c_events[k - 1].printEvent();
			}

			//System.out.println();

			c_size = k;

			for (i = 0; i < c_size; i++)
				events[i] = new Event(c_events[i]);
		}
	}

	public void track0()
	{
		int i = -1, j = -1, k = 0;

		c_events = new Event[size - 1];

		boolean undone = true;

		while (undone)
		{
			undone = false;

			k = 0;

			for (i = 0; i < c_size - 1; i++)
			{
				j = i + 1;
				while ((j < c_size) && (events[j].type == events[i].type))
					j++;

				c_events[k++] = new Event(events[i].type, events[i].start_time, events[j - 1].end_time, events[i].start_pos, events[j - 1].end_pos);
				c_events[k - 1].printEvent();

				i = j - 1;
			}

			if (c_size > 1)
			{
				if (events[c_size - 1].type != events[c_size - 2].type)
				{
					i = c_size - 1;
					c_events[k++] = new Event(events[i].type, events[i].start_time, events[i].end_time, events[i].start_pos, events[i].end_pos);
					c_events[k - 1].printEvent();
				}
			}
			else
			{
				c_events[k++] = new Event(events[0].type, events[0].start_time, events[0].end_time, events[0].start_pos, events[0].end_pos);
			}

			//System.out.println();

			c_size = k;

			for (i = 0; i < c_size; i++)
				events[i] = new Event(c_events[i]);

			k = 0;

			for (i = 0; i < c_size; i++)
			{
				if (!isValid(events[i].type))
				{
					char left = 'E';
					char right = 'E';
					if (i != 0)
						left = events[i - 1].type;
					if (i != c_size - 1)
						right = events[i + 1].type;

					double length = 0.0;
					double st = 0.0;
					double et = 0.0;
					double duration = 0.0;
					int sp = -1;
					int ep = -1;
					double rate = 0.0;

					if (events[i].type == 'F')
					{
						if (left == right)
						{
							char both = left;
							if ((both == 'G') || (both == 'H'))
							{
								// try 'G' both
								et = events[i + 1].end_time;
								st = events[i - 1].start_time;
								duration = et - st;
								sp = events[i - 1].start_pos;
								ep = events[i + 1].end_pos;
								length = lengths[ep] - lengths[sp];
								if (isGrowth(length, duration))
								{
									k--;
									c_events[k++] = new Event('G', st, et, sp, ep);
									c_events[k - 1].printEvent();
									i++;
									undone = true;
									continue;
								}
								// try 'A' none
								et = events[i].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
							}
							else if (both == 'A')
							{
								// try 'A' both
								et = events[i + 1].end_time;
								st = events[i - 1].start_time;
								duration = et - st;
								sp = events[i - 1].start_pos;
								ep = events[i + 1].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
							}
							else
							{
								// try 'A' none
								et = events[i].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									k--;
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									i++;
									undone = true;
									continue;
								}
							}
						}
						else
						{
							if ((left == 'G') || (left == 'H'))
							{
								// try 'G' left
								et = events[i].end_time;
								st = events[i - 1].start_time;
								duration = et - st;
								sp = events[i - 1].start_pos;
								ep = events[i].end_pos;
								length = lengths[ep] - lengths[sp];
								if (isGrowth(length, duration))
								{
									k--;
									c_events[k++] = new Event('G', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
								if (right == 'A')
								{
									// try 'A' right
									et = events[i + 1].end_time;
									st = events[i].start_time;
									duration = et - st;
									sp = events[i].start_pos;
									ep = events[i + 1].end_pos;
									length = attLength(sp, ep);
									rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
									if (isAttenuation(length, duration, rate))
									{
										c_events[k++] = new Event('A', st, et, sp, ep);
										c_events[k - 1].printEvent();
										i++;
										undone = true;
										continue;
									}
								}
								else
								{
									// try 'A' none
									et = events[i].end_time;
									st = events[i].start_time;
									duration = et - st;
									sp = events[i].start_pos;
									ep = events[i].end_pos;
									length = attLength(sp, ep);
									rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
									if (isAttenuation(length, duration, rate))
									{
										c_events[k++] = new Event('A', st, et, sp, ep);
										c_events[k - 1].printEvent();
										undone = true;
										continue;
									}
								}
							}
							else if ((right == 'G') || (right == 'H'))
							{
								// try 'G' right
								et = events[i + 1].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i + 1].end_pos;
								length = lengths[ep] - lengths[sp];
								if (isGrowth(length, duration))
								{
									c_events[k++] = new Event('G', st, et, sp, ep);
									c_events[k - 1].printEvent();
									i++;
									undone = true;
									continue;
								}
								if (left == 'A')
								{
									// try 'A' left
									et = events[i].end_time;
									st = events[i - 1].start_time;
									duration = et - st;
									sp = events[i - 1].start_pos;
									ep = events[i].end_pos;
									length = attLength(sp, ep);
									rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
									if (isAttenuation(length, duration, rate))
									{
										k--;
										c_events[k++] = new Event('A', st, et, sp, ep);
										c_events[k - 1].printEvent();
										undone = true;
										continue;
									}
								}
								else
								{
									// try 'A' none
									et = events[i].end_time;
									st = events[i].start_time;
									duration = et - st;
									sp = events[i].start_pos;
									ep = events[i].end_pos;
									length = attLength(sp, ep);
									rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
									if (isAttenuation(length, duration, rate))
									{
										c_events[k++] = new Event('A', st, et, sp, ep);
										c_events[k - 1].printEvent();
										undone = true;
										continue;
									}
								}
							}
							else
							{
								// try 'A' none
								et = events[i].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
							}
						}
					}
					else if (events[i].type == 'H')
					{
						if (left == right)
						{
							char both = left;
							if ((both == 'G') || (both == 'F'))
							{
								// try 'A' none
								et = events[i].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
								// try 'G' both
								et = events[i + 1].end_time;
								st = events[i - 1].start_time;
								duration = et - st;
								sp = events[i - 1].start_pos;
								ep = events[i + 1].end_pos;
								length = lengths[ep] - lengths[sp];
								if (isGrowth(length, duration))
								{
									k--;
									c_events[k++] = new Event('G', st, et, sp, ep);
									c_events[k - 1].printEvent();
									i++;
									undone = true;
									continue;
								}
							}
							else if (both == 'A')
							{
								// try 'A' both
								et = events[i + 1].end_time;
								st = events[i - 1].start_time;
								duration = et - st;
								sp = events[i - 1].start_pos;
								ep = events[i + 1].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									k--;
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									i++;
									undone = true;
									continue;
								}
							}
							else
							{
								// try 'A' none
								et = events[i].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
							}
						}
						else
						{
							if (left == 'A')
							{
								// try 'A' left
								et = events[i].end_time;
								st = events[i - 1].start_time;
								duration = et - st;
								sp = events[i - 1].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									k--;
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
							}
							else if (right == 'A')
							{
								// try 'A' right
								et = events[i + 1].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i + 1].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									i++;
									undone = true;
									continue;
								}
							}
							else if ((left == 'G') || (left == 'F'))
							{
								// try 'A' none
								et = events[i].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
								// try 'G' left
								et = events[i].end_time;
								st = events[i - 1].start_time;
								duration = et - st;
								sp = events[i - 1].start_pos;
								ep = events[i].end_pos;
								length = lengths[ep] - lengths[sp];
								if (isGrowth(length, duration))
								{
									k--;
									c_events[k++] = new Event('G', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
							}
							else if ((right == 'G') || (right == 'F'))
							{
								// try 'A' none
								et = events[i].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
								// try 'G' right
								et = events[i + 1].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i + 1].end_pos;
								length = lengths[ep] - lengths[sp];
								if (isGrowth(length, duration))
								{
									c_events[k++] = new Event('G', st, et, sp, ep);
									c_events[k - 1].printEvent();
									i++;
									undone = true;
									continue;
								}
							}
							else
							{
								// try 'A' none
								et = events[i].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
							}
						}
					}
					else if (events[i].type == 'R')
					{
						if (left == right)
						{
							char both = left;
							if ((both == 'S') || (both == 'T'))
							{
								// try 'S' both
								et = events[i + 1].end_time;
								st = events[i - 1].start_time;
								duration = et - st;
								sp = events[i - 1].start_pos;
								ep = events[i + 1].end_pos;
								length = lengths[ep] - lengths[sp];
								if (isShortening(length, duration))
								{
									k--;
									c_events[k++] = new Event('S', st, et, sp, ep);
									c_events[k - 1].printEvent();
									i++;
									undone = true;
									continue;
								}
								// try 'A' none
								et = events[i].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
							}
							else if (both == 'A')
							{
								// try 'A' both
								et = events[i + 1].end_time;
								st = events[i - 1].start_time;
								duration = et - st;
								sp = events[i - 1].start_pos;
								ep = events[i + 1].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
							}
							else
							{
								// try 'A' none
								et = events[i].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									k--;
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									i++;
									undone = true;
									continue;
								}
							}
						}
						else
						{
							if ((left == 'S') || (left == 'T'))
							{
								// try 'S' left
								et = events[i].end_time;
								st = events[i - 1].start_time;
								duration = et - st;
								sp = events[i - 1].start_pos;
								ep = events[i].end_pos;
								length = lengths[ep] - lengths[sp];
								if (isShortening(length, duration))
								{
									k--;
									c_events[k++] = new Event('S', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
								if (right == 'A')
								{
									// try 'A' right
									et = events[i + 1].end_time;
									st = events[i].start_time;
									duration = et - st;
									sp = events[i].start_pos;
									ep = events[i + 1].end_pos;
									length = attLength(sp, ep);
									rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
									if (isAttenuation(length, duration, rate))
									{
										c_events[k++] = new Event('A', st, et, sp, ep);
										c_events[k - 1].printEvent();
										i++;
										undone = true;
										continue;
									}
								}
								else
								{
									// try 'A' none
									et = events[i].end_time;
									st = events[i].start_time;
									duration = et - st;
									sp = events[i].start_pos;
									ep = events[i].end_pos;
									length = attLength(sp, ep);
									rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
									if (isAttenuation(length, duration, rate))
									{
										c_events[k++] = new Event('A', st, et, sp, ep);
										c_events[k - 1].printEvent();
										undone = true;
										continue;
									}
								}
							}
							else if ((right == 'S') || (right == 'T'))
							{
								// try 'S' right
								et = events[i + 1].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i + 1].end_pos;
								length = lengths[ep] - lengths[sp];
								if (isShortening(length, duration))
								{
									c_events[k++] = new Event('S', st, et, sp, ep);
									c_events[k - 1].printEvent();
									i++;
									undone = true;
									continue;
								}
								if (left == 'A')
								{
									// try 'A' left
									et = events[i].end_time;
									st = events[i - 1].start_time;
									duration = et - st;
									sp = events[i - 1].start_pos;
									ep = events[i].end_pos;
									length = attLength(sp, ep);
									rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
									if (isAttenuation(length, duration, rate))
									{
										k--;
										c_events[k++] = new Event('A', st, et, sp, ep);
										c_events[k - 1].printEvent();
										undone = true;
										continue;
									}
								}
								else
								{
									// try 'A' none
									et = events[i].end_time;
									st = events[i].start_time;
									duration = et - st;
									sp = events[i].start_pos;
									ep = events[i].end_pos;
									length = attLength(sp, ep);
									rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
									if (isAttenuation(length, duration, rate))
									{
										c_events[k++] = new Event('A', st, et, sp, ep);
										c_events[k - 1].printEvent();
										undone = true;
										continue;
									}
								}
							}
							else
							{
								// try 'A' none
								et = events[i].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
							}
						}
					}
					else if (events[i].type == 'T')
					{
						if (left == right)
						{
							char both = left;
							if ((both == 'S') || (both == 'R'))
							{
								// try 'A' none
								et = events[i].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
								// try 'S' both
								et = events[i + 1].end_time;
								st = events[i - 1].start_time;
								duration = et - st;
								sp = events[i - 1].start_pos;
								ep = events[i + 1].end_pos;
								length = lengths[ep] - lengths[sp];
								if (isShortening(length, duration))
								{
									k--;
									c_events[k++] = new Event('S', st, et, sp, ep);
									c_events[k - 1].printEvent();
									i++;
									undone = true;
									continue;
								}
							}
							else if (both == 'A')
							{
								// try 'A' both
								et = events[i + 1].end_time;
								st = events[i - 1].start_time;
								duration = et - st;
								sp = events[i - 1].start_pos;
								ep = events[i + 1].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									k--;
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									i++;
									undone = true;
									continue;
								}
							}
							else
							{
								// try 'A' none
								et = events[i].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
							}
						}
						else
						{
							if (left == 'A')
							{
								// try 'A' left
								et = events[i].end_time;
								st = events[i - 1].start_time;
								duration = et - st;
								sp = events[i - 1].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									k--;
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
							}
							else if (right == 'A')
							{
								// try 'A' right
								et = events[i + 1].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i + 1].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									i++;
									undone = true;
									continue;
								}
							}
							else if ((left == 'S') || (left == 'R'))
							{
								// try 'A' none
								et = events[i].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
								// try 'S' left
								et = events[i].end_time;
								st = events[i - 1].start_time;
								duration = et - st;
								sp = events[i - 1].start_pos;
								ep = events[i].end_pos;
								length = lengths[ep] - lengths[sp];
								if (isShortening(length, duration))
								{
									k--;
									c_events[k++] = new Event('S', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
							}
							else if ((right == 'S') || (right == 'R'))
							{
								// try 'A' none
								et = events[i].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
								// try 'S' right
								et = events[i + 1].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i + 1].end_pos;
								length = lengths[ep] - lengths[sp];
								if (isShortening(length, duration))
								{
									c_events[k++] = new Event('S', st, et, sp, ep);
									c_events[k - 1].printEvent();
									i++;
									undone = true;
									continue;
								}
							}
							else
							{
								// try 'A' none
								et = events[i].end_time;
								st = events[i].start_time;
								duration = et - st;
								sp = events[i].start_pos;
								ep = events[i].end_pos;
								length = attLength(sp, ep);
								rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;
								if (isAttenuation(length, duration, rate))
								{
									c_events[k++] = new Event('A', st, et, sp, ep);
									c_events[k - 1].printEvent();
									undone = true;
									continue;
								}
							}
						}
					}
				}

				c_events[k++] = new Event(events[i]);
				c_events[k - 1].printEvent();
			}

			//System.out.println();

			c_size = k;

			for (i = 0; i < c_size; i++)
				events[i] = new Event(c_events[i]);
		}
	}

	public boolean tryGrowthLeft(int index[])
	{
		int i = index[0];
		int k = index[1];

		double st = events[i - 1].start_time;
		double et = events[i].end_time;
		double duration = et - st;

		int sp = events[i - 1].start_pos;
		int ep = events[i].end_pos;
		double length = lengths[ep] - lengths[sp];

		boolean success = isGrowth(length, duration);

		if (success)
		{
			k--;
			c_events[k++] = new Event('G', st, et, sp, ep);
		}

		index[0] = i;
		index[1] = k;

		return success;
	}

	public boolean tryGrowthRight(int index[])
	{
		int i = index[0];
		int k = index[1];

		double st = events[i].start_time;
		double et = events[i + 1].end_time;
		double duration = et - st;

		int sp = events[i].start_pos;
		int ep = events[i + 1].end_pos;
		double length = lengths[ep] - lengths[sp];

		boolean success = isGrowth(length, duration);

		if (success)
		{
			c_events[k++] = new Event('G', st, et, sp, ep);
			i++;
		}

		index[0] = i;
		index[1] = k;

		return success;
	}

	public boolean tryGrowthBoth(int index[])
	{
		int i = index[0];
		int k = index[1];

		double st = events[i - 1].start_time;
		double et = events[i + 1].end_time;
		double duration = et - st;

		int sp = events[i - 1].start_pos;
		int ep = events[i + 1].end_pos;
		double length = lengths[ep] - lengths[sp];

		boolean success = isGrowth(length, duration);

		if (success)
		{
			k--;
			c_events[k++] = new Event('G', st, et, sp, ep);
			i++;
		}

		index[0] = i;
		index[1] = k;

		return success;
	}

	public boolean tryShorteningLeft(int index[])
	{
		int i = index[0];
		int k = index[1];

		double st = events[i - 1].start_time;
		double et = events[i].end_time;
		double duration = et - st;

		int sp = events[i - 1].start_pos;
		int ep = events[i].end_pos;
		double length = lengths[ep] - lengths[sp];

		boolean success = isShortening(length, duration);

		if (success)
		{
			k--;
			c_events[k++] = new Event('S', st, et, sp, ep);
		}

		index[0] = i;
		index[1] = k;

		return success;
	}

	public boolean tryShorteningRight(int index[])
	{
		int i = index[0];
		int k = index[1];

		double st = events[i].start_time;
		double et = events[i + 1].end_time;
		double duration = et - st;

		int sp = events[i].start_pos;
		int ep = events[i + 1].end_pos;
		double length = lengths[ep] - lengths[sp];

		boolean success = isShortening(length, duration);

		if (success)
		{
			c_events[k++] = new Event('S', st, et, sp, ep);
			i++;
		}

		index[0] = i;
		index[1] = k;

		return success;
	}

	public boolean tryShorteningBoth(int index[])
	{
		int i = index[0];
		int k = index[1];

		double st = events[i - 1].start_time;
		double et = events[i + 1].end_time;
		double duration = et - st;

		int sp = events[i - 1].start_pos;
		int ep = events[i + 1].end_pos;
		double length = lengths[ep] - lengths[sp];

		boolean success = isShortening(length, duration);

		if (success)
		{
			k--;
			c_events[k++] = new Event('S', st, et, sp, ep);
			i++;
		}

		index[0] = i;
		index[1] = k;

		return success;
	}

	public boolean tryAttenuationNone(int index[])
	{
		int i = index[0];
		int k = index[1];

		double st = events[i].start_time;
		double et = events[i].end_time;
		double duration = et - st;

		int sp = events[i].start_pos;
		int ep = events[i].end_pos;
		double length = attLength(sp, ep);

		double rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;

		boolean success = isAttenuation(length, duration, rate);

		if (success)
		{
			c_events[k++] = new Event('A', st, et, sp, ep);
		}

		index[0] = i;
		index[1] = k;

		return success;
	}

	public boolean tryAttenuationLeft(int index[])
	{
		int i = index[0];
		int k = index[1];

		double st = events[i - 1].start_time;
		double et = events[i].end_time;
		double duration = et - st;

		int sp = events[i - 1].start_pos;
		int ep = events[i].end_pos;
		double length = attLength(sp, ep);

		double rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;

		boolean success = isAttenuation(length, duration, rate);

		if (success)
		{
			k--;
			c_events[k++] = new Event('A', st, et, sp, ep);
		}

		index[0] = i;
		index[1] = k;

		return success;
	}

	public boolean tryAttenuationRight(int index[])
	{
		int i = index[0];
		int k = index[1];

		double st = events[i].start_time;
		double et = events[i + 1].end_time;
		double duration = et - st;

		int sp = events[i].start_pos;
		int ep = events[i + 1].end_pos;
		double length = attLength(sp, ep);

		double rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;

		boolean success = isAttenuation(length, duration, rate);

		if (success)
		{
			c_events[k++] = new Event('A', st, et, sp, ep);
			i++;
		}

		index[0] = i;
		index[1] = k;

		return success;
	}

	public boolean tryAttenuationBoth(int index[])
	{
		int i = index[0];
		int k = index[1];

		double st = events[i - 1].start_time;
		double et = events[i + 1].end_time;
		double duration = et - st;

		int sp = events[i - 1].start_pos;
		int ep = events[i + 1].end_pos;
		double length = attLength(sp, ep);

		double rate = (lengths[ep] - lengths[sp]) * 60.0 / duration;

		boolean success = isAttenuation(length, duration, rate);

		if (success)
		{
			k--;
			c_events[k++] = new Event('A', st, et, sp, ep);
			i++;
		}

		index[0] = i;
		index[1] = k;

		return success;
	}

	public boolean isGrowth(double length, double duration)
	{
		double rate = length * 60.0 / duration;

		//System.out.printf("isGrowth: %.2f %.2f %.2f\t", length, duration, rate);

		if ((rate >= COMPLEX_GROWTH_RATE) && (length >= COMPLEX_GROWTH_LENGTH))
		{
			//System.out.println(true);
			return true;
		}

		//System.out.println(false);
		return false;
	}

	public boolean isShortening(double length, double duration)
	{
		double rate = length * 60.0 / duration;

		//System.out.printf("isShortening: %.2f %.2f %.2f\t", length, duration, rate);

		if ((rate <= COMPLEX_SHORTENING_RATE) && (length <= COMPLEX_SHORTENING_LENGTH))
		{
			//System.out.println(true);
			return true;
		}

		//System.out.println(false);
		return false;
	}

	public boolean isAttenuation(double length, double duration, double rate)
	{
		//System.out.printf("isAttenuation: %.2f %.2f %.2f\t", length, duration, rate);

		if ((rate < COMPLEX_GROWTH_RATE) && (rate > COMPLEX_SHORTENING_RATE) && (duration >= COMPLEX_ATTENUATION_TIME) && (Math.abs(length) <= COMPLEX_ATTENUATION_LENGTH))
		{
			//System.out.println(true);
			return true;
		}

		//System.out.println(false);
		return false;
	}

	public boolean isValid(char c)
	{
		return ((c == 'G') || (c == 'S') || (c == 'A'));
	}

	public double attLength(int start, int end)
	{
		double al = 0.0;

		double max = 0.0;
		double min = 0.0;

		for (int i = start; i < end; i++)
		{
			double del = lengths[i + 1] - lengths[i];
			if (max < del)
				max = del;
			if (min > del)
				min = del;
		}

		if (max > -min)
			al = max;
		else // if (max <= -min)
			al = min;

		return al;
	}

	public int[][] getEvents()
	{
		int eventmatrix[][] = new int[c_size][3];

		int i = -1, j = -1;

		for (i = 0; i < c_size; i++)
		{
			Event e = events[i];

			if (e.type == 'G')
				eventmatrix[i][0] = 0;
			else if (e.type == 'S')
				eventmatrix[i][0] = 1;
			else if (e.type == 'A')
				eventmatrix[i][0] = 2;
			else
				//eventmatrix[i][0] = 3;
				eventmatrix[i][0] = 2;	// forcing 'E' to be 'A'

			eventmatrix[i][1] = e.start_pos;
			eventmatrix[i][2] = e.end_pos;
		}

		return eventmatrix;
	}
}


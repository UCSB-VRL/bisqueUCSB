import java.util.*;

public class Event
{
	public char type;
	public double start_time;
	public double end_time;
	//public double start_length;
	//public double end_length;
	//public double len;
	//public double rate;
	//public double duration;
	public int start_pos;
	public int end_pos;

	Event(char c, double st, double et, int sp, int ep)//, double sl, double el)
	{
		type = c;
		start_time = st;
		end_time = et;
		start_pos = sp;
		end_pos = ep;
		//start_length = sl;
		//end_length = el;
		//len = end_length - start_length;
		//duration = end_time - start_time;
		//rate = len * 60.0 / duration;
	}

	/*
	Event(char c, double st, double et, double l)
	{
		type = c;
		start_time = st;
		end_time = et;
		start_pos = -1;
		end_pos = -1;
		len = l;
		duration = end_time - start_time;
		rate = len * 60.0 / duration;
	}
	//*/

	Event(Event e)
	{
		type = e.type;
		start_time = e.start_time;
		end_time = e.end_time;
		start_pos = e.start_pos;
		end_pos = e.end_pos;
		//start_length = e.start_length;
		//end_length = e.end_length;
		//len = e.len;
		//duration = e.duration;
		//rate = e.rate;
	}

	public void printEvent()
	{
		//System.out.printf("%c: %.2f %.2f\n", type, start_time, end_time);
	}
}


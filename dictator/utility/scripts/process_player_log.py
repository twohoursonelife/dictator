with open('player-log.txt', 'r') as f:
    lines = f.readlines()

for l in lines:
    count = l.split()
    with open('player-count.txt', 'a') as f:
        f.write(f'{count[0]}\n')
    
    time = count[3].split('.')
    date = f'{count[2]} {time[0]}'

    with open('player-time.txt', 'a') as f:
        f.write(f'{date}\n')